import re
import json
from noob_snhubot import DB_CONFIG, slack_client
from BotHelper import Catalog, Course
from BotHelper.HashTable import HashTable

command = "catalog"
public = True
disabled = False

# Check if we're running with a database connection
if DB_CONFIG:
    # perform imports
    from noob_snhubot import mongo
    
    # change to catalog/subjects context
    mongo.use_db('catalog')
    mongo.use_collection('subjects')
    
    # get all documents
    data = mongo.find_documents({})

    # create Catalog using HashTable implementation
    catalog = Catalog()
    for subject in data:
        course_data = HashTable(47)
        for course in subject['courses']:
            course_data[course['id']] = Course(course['title'], course['description'], course['credits'], course['requisites'])
        catalog.subjects[subject['title']] = course_data
else:    
    disabled = True

def execute(command, user):
    bot_id = slack_client.api_call("auth.test")["user_id"]
    
    default_response = "Sorry, I don't understand. Try `<@{}> catalog help` for more details.".format(bot_id)
    response = None
    attachment = None

    if disabled:
        response = "I'm sorry. This command has been disabled because I'm currently running without a database connection."
    else:
        COURSE_FORMAT = "^[a-zA-Z]{2,3}-?[0-9]{3}" # CS499, ACC-101, etc
        requests = command.split()        

        if len(requests) > 1:
            if requests[1].lower().startswith('help'):
                response = "There's two ways I can help you:\n`catalog <Subject>` will return a list of course IDs for a given subject: `catalog Computer Science`\n`catalog <Course ID>` will give you details about a given course: `catalog CS499`\nYou can also feed me a list of up to three courses, and I'll try to find all of them: `catalog CS200 CS201 CS260`"
            elif re.match(COURSE_FORMAT, requests[1]):
                # process course list
                attachments = []
                bad_courses = []
                
                # get only 3 courses from list
                for course in requests[1:4]:
                    course = course.upper()                    
                    match = re.match(COURSE_FORMAT, course)                    

                    if match is not None:                                                
                        course = course.replace("-", "") # Strip the dash
                        course_data = catalog.get_course(course)

                        if course_data:                    
                            attach = {
                                "title":"{}".format(course_data.title),
                                "fields":[                                
                                    {
                                        "title":"Description",
                                        "value":"{}".format(course_data.description)
                                    },
                                    {
                                        "title":"Course ID",
                                        "value":"{}".format(course),
                                        "short":"true"
                                    },
                                    {
                                        "title":"Credits",
                                        "value":"{}".format(course_data.credits),
                                        "short":"true"
                                    }
                                ],
                                "color":"#0a3370", #notice the SNHU Color Scheme!
                                "footer":"Brought to you by SNHU",
			                    "footer_icon":"https://www.snhu.edu/assets/SNHU/images/common/favicon.ico"
                            }

                            if course_data.requisites:
                                attach['fields'].append({
                                    "title":"Requisites",
                                    "value":"{}".format(course_data.requisites)
                                })                              

                            attachments.append(attach)
                        else:                            
                            bad_courses.append(course)

                if bad_courses:
                    bad_course_attachment = {
                        "title":"Failed Course IDs",
                        "text":"{}".format(', '.join(bad_courses)),
                        "color":"warning"
                    }

                    attachments.append(bad_course_attachment)
                
                attachment = json.dumps(attachments)
            else:
                # process subject
                for key in catalog.subjects.keys():
                    if ' '.join(requests[1:]).title().startswith(key):
                        subject = catalog.get_subject(key)
                        response = "Here is a list of Course IDs for *{}*:\n{}".format(key, ', '.join(subject.keys()))

    return response or default_response, attachment
