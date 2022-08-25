# flake8: noqa
from django.utils.translation import gettext_noop

STATICALLY_ANALYZABLE_TRANSLATIONS = [
    gettext_noop('1 Day'),
    gettext_noop('1 hour'),
    gettext_noop('1.x'),
    gettext_noop('1.0'),
    gettext_noop('1.5'),
    gettext_noop('10'),
    gettext_noop('12 hours'),
    gettext_noop('15 minutes'),
    gettext_noop('160'),
    gettext_noop('2 hours'),
    gettext_noop('2.0'),
    gettext_noop('2.x'),
    gettext_noop('20'),
    gettext_noop('24 hours'),
    gettext_noop('30 minutes'),
    gettext_noop('4 hours'),
    gettext_noop('40'),
    gettext_noop('5 Days'),
    gettext_noop('5'),
    gettext_noop('6 hours'),
    gettext_noop('8 hours'),
    gettext_noop('80'),
    gettext_noop('Admin Password'),
    gettext_noop('Advanced'),
    gettext_noop('After login, the application will look at the profile\'s defined reference for the authoritative location of the newest version. This check will occur with some periodicity since the last successful check based on this property. freq-never disables the automatic check.'),
    gettext_noop('Allow mobile workers in the same case sharing group to share case lists.  Read more on the <a href="https://help.commcarehq.org/display/commcarepublic/Case+Sharing">Help Site</a>'),
    gettext_noop('Allow mobile workers to access the web-based version of your application. Read more on the <a href="https://help.commcarehq.org/display/commcarepublic/Using+Web+Apps">Help Site</a>'),
    gettext_noop('Allow visitors to use this application without a login.'),
    gettext_noop('Alphanumeric'),
    gettext_noop('Amount of time previously submitted forms remain accessible in the CommCare app.'),
    gettext_noop('Android app dependencies'),
    gettext_noop('Android Settings'),
    gettext_noop('Anonymous Usage'),
    gettext_noop('Any positive integer. Represents period of purging in days.'),
    gettext_noop('App Aware Location Fixture Format'),
    gettext_noop('App Version'),
    gettext_noop('Audio'),
    gettext_noop('Auto Capture Location<br />(all forms)'),
    gettext_noop('Auto Update Frequency'),
    gettext_noop('Auto-Resize Images'),
    gettext_noop('Auto-Sync Frequency'),
    gettext_noop('Auto-login'),
    gettext_noop('Auto-manage URLs'),
    gettext_noop('Automatic'),
    gettext_noop('Automatically resizes images within forms. Follow <a href=\'https://confluence.dimagi.com/display/commcarepublic/Auto-Resize+Images+on+Android\'> the instructions here</a> to determine which value to use.'),
    gettext_noop('Automatically trigger a two-way sync on a regular schedule'),
    gettext_noop('Basic'),
    gettext_noop('Both Hierarchical and Flat Fixture'),
    gettext_noop('Build Settings'),
    gettext_noop('Case Sharing'),
    gettext_noop('Choose an image to replace the default CommCare Home Screen logo'),
    gettext_noop('Choose to label the login buttons with Icons or Text'),
    gettext_noop('Choose whether or not mobile workers can view previously submitted forms.'),
    gettext_noop('Choose whether or not to display the \'Incomplete\' button on the ODK home screen'),
    gettext_noop('CommCare'),
    gettext_noop('CommCare Home Screen Logo'),
    gettext_noop('CommCare LTS'),
    gettext_noop('CommCare Sense'),
    gettext_noop('CommCare Version'),
    gettext_noop('Configure for low-literate users, J2ME only'),
    gettext_noop('Configure form menus display. For per-module option turn on grid view for the form\'s menu in a module under module\'s settings page. Read more on the <a target="_blank" href="https://help.commcarehq.org/display/commcarepublic/Grid+View+for+Form+and+Module+Screens">Help Site</a>.'),
    gettext_noop('Custom Base URL'),
    gettext_noop('Custom Keys'),
    gettext_noop('Custom Suite File'),
    gettext_noop('Custom Suite'),
    gettext_noop('Daily Log Sending Frequency'),
    gettext_noop('Daily'),
    gettext_noop('Data and Sharing'),
    gettext_noop('Days allowed without syncing before triggering a warning'),
    gettext_noop('Days for Review'),
    gettext_noop('Default Map Tileset'),
    gettext_noop('Demo Logo'),
    gettext_noop('Determines if the server automatically attempts to send data to the phone (Two-Way), or only attempt to send data on demand (Push Only); projects using Case Sharing should choose Two-Way. If set to Push Only, the Auto-Sync Frequency and Unsynced Time Limit settings will have no effect.'),
    gettext_noop('Determines whether phone keys will type letters or numbers by default when typing in the password field.'),
    gettext_noop('Disable'),
    gettext_noop('Disabled'),
    gettext_noop('Display root menu as a list or grid. Read more on the <a target="_blank" href="https://help.commcarehq.org/display/commcarepublic/Grid+View+for+Form+and+Module+Screens">Help Site</a>.'),
    gettext_noop('Enable Menu Display Setting Per-Module'),
    gettext_noop('Enable'),
    gettext_noop('Enabled'),
    gettext_noop('Extra Key Action'),
    gettext_noop('For mobile map displays, chooses a base tileset for the underlying map layer'),
    gettext_noop('Form Entry Style'),
    gettext_noop('Forms Menu Display'),
    gettext_noop('Forms are Never Removed'),
    gettext_noop('Full Keyboard'),
    gettext_noop('Full Resize'),
    gettext_noop('Full'),
    gettext_noop('Fuzzy Search'),
    gettext_noop('General Settings'),
    gettext_noop('Generic'),
    gettext_noop('Grid'),
    gettext_noop('Half Resize'),
    gettext_noop('High Density'),
    gettext_noop('Horizontal Resize'),
    gettext_noop('How Send All Unsent functionality is presented to the user'),
    gettext_noop('How often CommCare mobile should attempt to check for a new, released application version.'),
    gettext_noop('How often the phone should attempt to purge any cached storage which may have expired'),
    gettext_noop('Hybrid'),
    gettext_noop('Icons'),
    gettext_noop('If automatic is enabled, forms will attempt to send on their own without intervention from the user. If manual is enabled, the user must manually decide when to attempt to send forms.'),
    gettext_noop('If multimedia validation is enabled, CommCare will perform an additional check after installing your app to ensure that all of your multimedia is present on the phone before allowing the app to run. It is recommended for deployment, but will make your app unable to run if multimedia is enabled.'),
    gettext_noop('Image Compatibility on Multiple Devices'),
    gettext_noop('In normal mode, users log in each time with their username and password. In auto-login mode, once a user (not the \'admin\' or \'demo\' users) has logged in, the application will start up with that user already logged in.'),
    gettext_noop('Incomplete Forms'),
    gettext_noop('Item Selection Mode'),
    gettext_noop('Java Phone General Settings'),
    gettext_noop('Java Phone Platform'),
    gettext_noop('Java Phone User Interface Settings'),
    gettext_noop('Just One Day'),
    gettext_noop('Language cycles through any available translations. Audio plays the question\'s audio if available. NOTE: If audio is selected, a question\'s audio will not be played by default when the question is displayed.'),
    gettext_noop('Languages'),
    gettext_noop('Length of time after which you will be logged out automatically'),
    gettext_noop('List'),
    gettext_noop('Load video files lazily'),
    gettext_noop('Location Fixture format that is provided in the restore for this app'),
    gettext_noop('Log Case Detail Views'),
    gettext_noop('Logging Enabled'),
    gettext_noop('Login Buttons'),
    gettext_noop('Login Duration'),
    gettext_noop('Login Logo'),
    gettext_noop('Loose Media Mode'),
    gettext_noop('Loose'),
    gettext_noop('Low Density'),
    gettext_noop('Make OTA app updates skip download for video files at app update time.'),
    gettext_noop('Manual'),
    gettext_noop('Medium Density'),
    gettext_noop('Minimum duration between updates to mobile report data (hours).'),
    gettext_noop('Mobile Reports Update Frequency'),
    gettext_noop('Mobile UCR Restore Version'),
    gettext_noop('Modules Menu Display'),
    gettext_noop('Multimedia Validation'),
    gettext_noop('Multiple Questions per Screen displays a running list of questions on the screen at the same time. One Question per Screen displays each question independently. Note: OQPS does not support some features'),
    gettext_noop('Multiple Questions per Screen'),
    gettext_noop('Must correspond to the password format specified below.'),
    gettext_noop('Native (International)'),
    gettext_noop('Never'),
    gettext_noop('No (NOT RECOMMENDED)'),
    gettext_noop('No Users Mode'),
    gettext_noop('No Validation'),
    gettext_noop('No'),
    gettext_noop('Nokia S40 (default)'),
    gettext_noop('Nokia S60'),
    gettext_noop('None'),
    gettext_noop('Normal Scrolling'),
    gettext_noop('Normal'),
    gettext_noop('Number of unsent forms on phone before triggering warning text'),
    gettext_noop('Numeric Selection mode will display information about questions for longer and require more input from the user. Normal Scrolling will proceed to the next question whenever enough information is provided.'),
    gettext_noop('Numeric Selection'),
    gettext_noop('Numeric'),
    gettext_noop('OTA Restore Tolerance'),
    gettext_noop('Off'),
    gettext_noop('On CommCare Android, have this form automatically capture the user\'s current geo-location.\n'),
    gettext_noop('On'),
    gettext_noop('Once a Month'),
    gettext_noop('Once a Week'),
    gettext_noop('One Month'),
    gettext_noop('One Question per Screen'),
    gettext_noop('One Week'),
    gettext_noop('One Year'),
    gettext_noop('Only Flat Fixture'),
    gettext_noop('Only Hierarchical Fixture'),
    gettext_noop('Oops! This setting has been discontinued. We recommend you change this setting to Version 2, and it will no longer appear on your settings page.'),
    gettext_noop('Password Format'),
    gettext_noop('Practice Mobile Worker'),
    gettext_noop('Prevents mobile workers from using a CommCare app until the '
                 'Android apps that it needs have been installed on the '
                 'device.\n'),
    gettext_noop('Profile URL'),
    gettext_noop('Project Default'),
    gettext_noop('Prompt Updates to Latest CommCare Version'),
    gettext_noop('Prompt Updates to Latest Released App Version'),
    gettext_noop('Purge Frequency'),
    gettext_noop('Push Only'),
    gettext_noop('Required'),
    gettext_noop('Restrict this app to the selected CommCare flavor'),
    gettext_noop('Roman'),
    gettext_noop('Saved Forms'),
    gettext_noop('Satellite'),
    gettext_noop('Select the mobile worker to use as a practice user for this application'),
    gettext_noop('Send Data Over HTTP'),
    gettext_noop('Send Data'),
    gettext_noop('Send Forms Mode'),
    gettext_noop('Server User Registration'),
    gettext_noop('Set to skip if your deployment does not require users to register with the server. Note that this will likely result in OTA Restore and other features being unavailable.'),
    gettext_noop('Short'),
    gettext_noop('Simple (FOR TESTING ONLY: crashes with any unrecognized user-defined translations)'),
    gettext_noop('Skip'),
    gettext_noop('Strict'),
    gettext_noop('Sync Mode'),
    gettext_noop('Target CommCare Flavor'),
    gettext_noop('Terrain'),
    gettext_noop('Text Input'),
    gettext_noop('Text'),
    gettext_noop("The kind of Java phone you want to run the application on"),
    gettext_noop('This value will set whether the login screen uses customizable icons for login and demo mode options or uses the standard buttons with labels.'),
    gettext_noop('This will determine how images you select for your questions will be resized to fit the screen. Horizontal will stretch/compress the image to fit perfectly horizontally while scaling to height to maintain the aspect ratio. Full Resize will try to be clever and find the ideal vertical/horizontal scaling for the screen. Half Resize will do the same but with half the area.'),
    gettext_noop('This will set the amount of time you will remain logged in before automatically being logged out.'),
    gettext_noop('This will show or hide the \'Incomplete\' button on the CommCare ODK home screen. Turning this off will prevent users from saving incomplete forms.'),
    gettext_noop('This will show or hide the \'Saved\' button on the CommCare ODK home screen. Turning this off will prevent users from saving forms locally.'),
    gettext_noop('Three Months'),
    gettext_noop('Translations Strategy'),
    gettext_noop('Twice a Month'),
    gettext_noop('Two Weeks'),
    gettext_noop('Two-Way Sync'),
    gettext_noop('Unsent Form Limit'),
    gettext_noop('Unsynced Time Limit'),
    gettext_noop('Update on every sync'),
    gettext_noop('Upload a file to serve as a demo logo on Android phones'),
    gettext_noop('Upload a file to serve as a login logo on Android phones'),
    gettext_noop('Upload a file to serve as an app logo in Web Apps'),
    gettext_noop('Use Secure Submissions'),
    gettext_noop('Use project level setting'),
    gettext_noop('Use a different base URL for all app URLs. This makes the phone send forms, sync, and look for updates from a different URL. The main use case is to allow migrating project spaces to a new environment.\n'),
    gettext_noop('User Login Mode'),
    gettext_noop('Validate Multimedia'),
    gettext_noop('Version 1 translations (old)'),
    gettext_noop('Version 2 translations (recommended)'),
    gettext_noop('Version of mobile UCRs to use. Read more on the  <a target="_blank" href="https://help.commcarehq.org/display/saas/Moving+to+Mobile+UCR+V2">Help Site</a>'),
    gettext_noop('We frequently release new versions of CommCare Mobile. Use the latest version to take advantage of new features and bug fixes. Note that if you are using CommCare for Android you must also update your version of CommCare from the Google Play Store.'),
    gettext_noop('We suggest moving to CommCare 2.0 and above, unless your project is using referrals'),
    gettext_noop('Web App'),
    gettext_noop('Web Apps Logo'),
    gettext_noop('Weekly Log Sending Frequency'),
    gettext_noop('Weekly'),
    gettext_noop("What characters to allow users to input"),
    gettext_noop('What kind of log transmission the phone should attempt on a daily basis (submitted to PostURL)'),
    gettext_noop('What kind of log transmission the phone should attempt on a weekly basis (submitted to PostURL)'),
    gettext_noop('What the \'Extra Key\' (# on Nokia Phones) does when pressed'),
    gettext_noop('What user interface style should be used during form entry.'),
    gettext_noop('When a value is selected, this feature controls the display size of any user-provided image such that it will be consistent with the size of the original image file, and consistent across devices. Follow <a href=\'https://confluence.dimagi.com/display/commcarepublic/Image+Sizing+with+Multiple+Android+Device+Models\'> the instructions here</a> to determine which value to use.'),
    gettext_noop('When auto-sync is enabled CommCare will attempt to submit forms and synchronize the user\'s data after logging in with the frequency chosen.'),
    gettext_noop('When loose media mode is set to yes, CommCare will search for alternative media formats for any media that it cannot play. If CommCare attempts to play a file at jr://file/media/prompt_one.mp3 and mp3 files are not supported, the media directory will be searched for other files named prompt_one with alternative extensions which may be supported, for instance prompt_one.wav, and play that instead.'),
    gettext_noop('When the phone has this number of unsynced forms stored locally CommCare will trigger a warning'),
    gettext_noop('When this many days have passed without the user syncing CommCare will trigger a warning'),
    gettext_noop('When you select this box, your data will no longer be encrypted.  Because of changes regarding Java phone security certificates, it will be necessary to send data over HTTP to continue sending data to CommCare.'),
    gettext_noop('Whenever Possible'),
    gettext_noop('Whether CommCare should search for alternative formats of incompatible media files.'),
    gettext_noop('Whether CommCare should validate that all external multimedia is installed before letting the user run the app.'),
    gettext_noop('Whether OTA Restore is tolerant of failures, ambiguity, duplicate registrations, etc (and proceeds as best it can), or whether it fails immediately in these cases.'),
    gettext_noop('Whether form entry is optimized for speed, or for new users.'),
    gettext_noop('Whether logging of incidents should be activated on the client.'),
    gettext_noop('Whether or not the phone collects, saves, and sends data.'),
    gettext_noop('Whether searches can match similar strings'),
    gettext_noop('Whether searches on the phone will match similar strings. IE: \'Jhon\' will match \'John\''),
    gettext_noop('Whether to log each time a user views case details. May reduce mobile performance.'),
    gettext_noop('Whether to show the user login screen'),
    gettext_noop('Whether users registered on the phone need to be registered with the submission server.'),
    gettext_noop('WinMo'),
    gettext_noop('X-High Density'),
    gettext_noop('XX-High Density'),
    gettext_noop('XXX-High Density'),
    gettext_noop('Yes'),
    gettext_noop('disabled'),
    gettext_noop('Enable Text To Speech'),
    gettext_noop('Adds a text to speech button for all questions to read out the question text aloud.'),
    gettext_noop('Enable asterisk on required question'),
    gettext_noop('Adds a red asterisk to denote mandatory questions in a form. This setting only works in mobile.'),
]
