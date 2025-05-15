__artifacts_v2__ = {
    "NYC_Transit_Searches": {
        "name": "NYC Transit: MTA Subway & Bus",
        "description": "Parses dates and location data for searched locations using the NYC Transit App.",
        "author": "Joseph Dean",
        "version": "0.0.1",
        "date": "2025-05-09",
        "requirements": "none",
        "category": "Location",
        "notes": "There may be additonal locations in the list of 'Legs' and the group.com.busexpertapp.useast.newyork.plist",
        "paths": ('*/AppDomainGroup-group.com.busexpertapp.useast.newyork/2020-09.sqlite3*'),
        "function": "get_nyctransit_searches"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_nyctransit_searches(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('2020-09.sqlite3'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            #SQL QUERY TIME! START YOUR QUERY AT THE SELECT STATEMENT. ITS A REQUIREMENT TO HAVE YOUR TIMESTAMPE FIRST FOR LEAPP ARTIFACTS
            cursor.execute('''
            SELECT
            
            revisions.create_date AS "Timestamp",
            revisions.action AS "Action",            
            json_extract(revisions.value, '$.id') AS "Search ID",
            json_extract(revisions.value, '$.title') AS "Title",
            json_extract(revisions.value, '$.subtitle') AS "Subtitle",
            json_extract(revisions.value, '$.coordinate.latitude') AS "Latitude",
            json_extract(revisions.value, '$.coordinate.longitude') AS "Longitude"
            FROM revisions
            WHERE revisions.key LIKE "%search%"
            ORDER BY revisions.key
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                #    last_mod_date = row[0]
                #   if last_mod_date is None:
                #       pass
                #   else:
                #       last_mod_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_mod_date),time_offset)
                
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))#**IMPORTANT THIS IS FOR HOW MANY TABLES ARE LISTED IN YOUR QUERY. IS MORE THAN 7 ADD MORE ROW, IF LESS REMOVE ROW. ROW MUST START AT ROW 0
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Latitude and Longitude for searched items.' #THIS SHOWS UP ON THE REPORT SIDE
        report = ArtifactHtmlReport('NYC Transit: MTA Subway & Bus')#THIS IS WHAT SHOWS UP ON THE RIGHT SIDE OF THE HTML REPORT
        report.start_artifact_report(report_folder, 'NYC_Transit_Searches', description)
        report.add_script()
        data_headers = ('Timestamp','Action','Search ID','Title','Subtitle','Latitude','Longitude')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'NYC_Transit_Trips'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'NYC_Transit_Trips'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No NYC_Transit_Searches Found')#if not found in extractions, this is where it logs it wasn't found. update the name.
