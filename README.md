Unfuddle API http://unfuddle.com/support/docs/api

AgileZEN API http://dev.agilezen.com/

This package will aid in exporting tickets in unfuddle to stories and tasks in AgileZen

modify the settings.txt file to include you API credentials

    [Unfuddle]
    site: UNFUDDLESITENAME
    user: USERNAME
    pass: PASSWORD

    [Agilezen]
    apikey: AGILEZEN API KEY


Currently we only have one method -> export a all active tickets for a milestone to a new story in agilezen.