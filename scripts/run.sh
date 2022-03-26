#! /bin/bash
set -e

VALID_TEST_SUITES=(
    javascript
    python
    python-sharded
    python-sharded-and-javascript
    python-elasticsearch-v5
)


function setup {
    [ -n "$1" ] && TEST="$1"
    logmsg INFO "performing setup..."

    [ ! -f localsettings.py ] && rm *.log || true

    # prefer https for git checkouts made by pip
    git config --global url."https://".insteadOf git://

    pip install pip-tools
    pip-sync requirements/test-requirements.txt
    pip check  # make sure there are no incompatibilities in test-requirements.txt
    python_preheat  # preheat the python libs

    # compile pyc files
    python -m compileall -q corehq custom submodules testapps *.py

    if [[ "$TEST" =~ ^python ]]; then
        keytool -genkey \
            -keyalg RSA \
            -keysize 2048 \
            -validity 10000 \
            -alias javarosakey \
            -keypass onetwothreefourfive \
            -keystore InsecureTestingKeyStore \
            -storepass onetwothreefourfive \
            -dname 'CN=Foo, OU=Bar, O=Bizzle, L=Bazzle, ST=Bingle, C=US'
    fi

    if [ "$TEST" = "javascript" -o "$JS_SETUP" = "yes" ]; then
        # make sure to set in mocha-headless-chrome options
        #   executablePath: 'google-chrome-unstable'
        export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
        sudo npm -g install yarn bower grunt-cli uglify-js puppeteer mocha-headless-chrome
        yarn install --progress=false --frozen-lockfile
    fi

    scripts/docker hqtest up -d
    docker/wait.sh

    if [ ! -f localsettings.py ]; then
        ln -s docker/localsettings.py localsettings.py

        # cleanup dev environment without localsettings.py
        trap 'rm localsettings.py' EXIT
    fi
}

function python_preheat {
    # Perform preflight operations as the container's root user to "preheat"
    # libraries used by Django.
    #
    # Import the `eulxml.xmlmap` module which checks if its lextab module
    # (.../eulxml/xpath/lextab.py) is up-to-date and writes a new lextab.py file
    # if not. This write fails if performed by the container's cchq user due to
    # insufficient filesystem permissions at that path. E.g.
    #   WARNING: Couldn't write lextab module 'eulxml.xpath.lextab'. [Errno 13] Permission denied: '/vendor/lib/python3.6/site-packages/eulxml/xpath/lextab.py'
    #
    # NOTE: This "preheat" can also be performed by executing a no-op manage
    # action (e.g. `manage.py test -h`), but this operation is heavy-handed and
    # importing the python module directly is done instead to improve
    # performance.
    logmsg INFO "preheating python libraries"
    # send to /dev/null and allow to fail
    python -c 'import eulxml.xmlmap' >/dev/null 2>&1 || true
}

function tests {
    # Disabled due to: https://github.com/github/feedback/discussions/8848
    # [ -n "$GITHUB_ACTIONS" ] && echo "::endgroup::"  # "Docker setup" begins in scripts/docker
    TEST="$1"
    shift
    suite_pat=$(printf '%s|' "${VALID_TEST_SUITES[@]}" | sed -E 's/\|$//')
    if ! echo "$TEST" | grep -E "^(${suite_pat})$" >/dev/null; then
        logmsg ERROR "invalid test suite: $TEST (choices=${suite_pat})"
        exit 1
    fi

    log_group_begin "Django test suite setup"
    setup_start=$(date +%s)
    setup "$TEST"
    delta=$(($(date +%s) - $setup_start))
    log_group_end

    send_timing_metric_to_datadog "setup" $delta

    log_group_begin "Django test suite: $TEST"
    tests_start=$(date +%s)
    argv_str=$(printf ' %q' "$TEST" "$@")

    py_test_args=("$@")
    js_test_args=("$@")
    case "$TEST" in
        python-sharded*)
            export USE_PARTITIONED_DATABASE=yes
            # TODO make it possible to run a subset of python-sharded tests
            py_test_args+=("--attr=sharded")
            ;;
        python-elasticsearch-v5)
            export ELASTICSEARCH_HOST='elasticsearch5'
            export ELASTICSEARCH_PORT=9205
            export ELASTICSEARCH_MAJOR_VERSION=5
            py_test_args+=("--attr=es_test")
            ;;
    esac

    function _test_python {
        ./manage.py create_kafka_topics
        if [ -n "$CI" ]; then
            logmsg INFO "coverage run manage.py test ${py_test_args[*]}"
            # `coverage` generates a file that's then sent to codecov
            coverage run manage.py test "${py_test_args[@]}"
            coverage xml
            if [ -n "$TRAVIS" ]; then
                bash <(curl -s https://codecov.io/bash)
            fi
        else
            logmsg INFO "./manage.py test ${py_test_args[*]}"
            ./manage.py test "${py_test_args[@]}"
        fi
    }

    function _test_javascript {
        ./manage.py migrate --noinput
        ./manage.py runserver 0.0.0.0:8000 &> commcare-hq.log &
        scripts/wait.sh 127.0.0.1:8000
        logmsg INFO "grunt test ${js_test_args[*]}"
        grunt test "${js_test_args[@]}"
    }

    case "$TEST" in
        python-sharded-and-javascript)
            _test_python
            _test_javascript
            ./manage.py static_analysis
            ;;
        python|python-sharded|python-elasticsearch-v5)
            _test_python
            ;;
        javascript)
            _test_javascript
            ;;
        *)
            # this should never happen (would mean there is a bug in this script)
            logmsg ERROR "invalid TEST value: '${TEST}'"
            exit 1
            ;;
    esac

    log_group_end  # only log group end on success (notice: `set -e`)
    [ "$TEST" == "python-sharded-and-javascript" ] && scripts/test-make-requirements.sh
    [ "$TEST" == "python-sharded-and-javascript" -o "$TEST_MIGRATIONS" ] && scripts/test-django-migrations.sh
    [ "$TEST" == "python-sharded-and-javascript" ] && scripts/track-dependency-status.sh
    delta=$(($(date +%s) - $tests_start))

    send_timing_metric_to_datadog "tests" $delta
    send_counter_metric_to_datadog
}

function send_timing_metric_to_datadog() {
    send_metric_to_datadog "travis.timings.$1" $2 "gauge" "test_type:$TEST"
}

function send_counter_metric_to_datadog() {
    send_metric_to_datadog "travis.count" 1 "counter" "test_type:$TEST"
}

function bootstrap {
    export CCHQ_IS_FRESH_INSTALL=1 &&
        ./manage.py sync_couch_views &&
        ./manage.py migrate --noinput &&
        ./manage.py compilejsi18n &&
        ./manage.py create_kafka_topics &&
        ./manage.py make_superuser admin@example.com
}

function runserver {
    su cchq -c "./manage.py runserver $@ 0.0.0.0:8000"
}

source scripts/datadog-utils.sh  # provides send_metric_to_datadog
source scripts/bash-utils.sh  # provides logmsg, log_group_{begin,end}, func_text and truthy

logmsg INFO "running: $*"
"$@"
