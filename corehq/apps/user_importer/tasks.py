import functools

from celery.exceptions import TimeoutError
from celery.task import task

from django.db import DEFAULT_DB_ALIAS

from dimagi.utils.chunked import chunked

from soil import DownloadBase
from soil.progress import get_task_progress

from corehq.apps.users.models import WebUser
from corehq.apps.user_importer.models import UserUploadRecord


USER_UPLOAD_CHUNK_SIZE = 1000


@task(bind=True)
def import_users_and_groups(self, domain, user_specs, group_specs, upload_user_id, upload_record_id, is_web_upload,
                            task_id=None):
    from corehq.apps.user_importer.importer import create_or_update_commcare_users_and_groups, \
        create_or_update_groups, create_or_update_web_users
    if task_id is None:
        task_id = self.request.id
    DownloadBase.set_progress(self, 0, 100, task_id)

    total = len(user_specs) + len(group_specs)
    DownloadBase.set_progress(self, 0, total, task_id)

    group_memoizer, group_results = create_or_update_groups(domain, group_specs)

    DownloadBase.set_progress(self, len(group_specs), total, task_id)

    def _update_progress(value, start=0):
        DownloadBase.set_progress(self, start + value, total, task_id)

    upload_user = WebUser.get_by_user_id(upload_user_id)
    if is_web_upload:
        user_results = create_or_update_web_users(
            domain,
            user_specs,
            upload_user=upload_user,
            upload_record_id=upload_record_id,
            update_progress=functools.partial(_update_progress, start=len(group_specs))
        )
    else:
        user_results = create_or_update_commcare_users_and_groups(
            domain,
            user_specs,
            upload_user=upload_user,
            upload_record_id=upload_record_id,
            group_memoizer=group_memoizer,
            update_progress=functools.partial(_update_progress, start=len(group_specs))
        )
    results = {
        'errors': group_results['errors'] + user_results['errors'],
        'rows': user_results['rows']
    }
    upload_record = UserUploadRecord.objects.using(DEFAULT_DB_ALIAS).get(pk=upload_record_id)
    upload_record.task_id = task_id
    upload_record.result = results
    upload_record.save()
    DownloadBase.set_progress(self, total, total, task_id)
    return {
        'messages': results
    }


@task(queue='ush_background_tasks', bind=True)
def parallel_import_task(self, domain, user_specs, group_specs, upload_user_id,
                         upload_record_id, is_web_user_upload=False):
    task_id = self.request.id
    return import_users_and_groups(domain, user_specs, group_specs, upload_user_id, upload_record_id,
                                   is_web_user_upload, task_id)


@task(queue='ush_background_tasks')
def parallel_user_import(domain, user_specs, upload_user_id):
    task = parallel_user_import
    total = len(user_specs)
    DownloadBase.set_progress(task, 0, total)
    task_list = []
    for users in chunked(user_specs, USER_UPLOAD_CHUNK_SIZE):
        upload_record = UserUploadRecord(
            domain=domain,
            user_id=upload_user_id
        )
        upload_record.save()

        subtask = parallel_import_task.delay(
            domain,
            list(users),
            [],
            upload_user_id,
            upload_record.pk
        )
        task_list.append(subtask)

    incomplete = True
    while incomplete:
        subtask_progress = 0
        incomplete = False
        for subtask in task_list:
            try:
                subtask.get(timeout=1, disable_sync_subtasks=False)
            except TimeoutError:
                incomplete = True
                subtask_progress += get_task_progress(subtask).current or 0
            else:
                # The task is done, just count the rows in the result
                subtask_progress += len(subtask.result['messages']['rows'])
        DownloadBase.set_progress(task, subtask_progress, total)

    # all tasks are done, collect results
    rows = []
    errors = []
    for subtask in task_list:
        rows.extend(subtask.result['messages']['rows'])
        errors.extend(subtask.result['messages']['errors'])

    messages = {
        'rows': rows,
        'errors': errors
    }

    return {
        'messages': messages
    }
