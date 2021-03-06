from optparse import make_option
from django.core.management.base import BaseCommand
from ...helpers import get_full_address, write_error, find_title
from master_schedule.models import Masterschoolschedule, Course, Teacherschedule, Hrsbio, Roomcatalog, \
                                   Schoolcycle, Schoolperiods, Gradelevel, Terms
import csv
from datetime import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--long', '-l', dest='long',
                    help='Help for the long options'),
        make_option('--action', '-a',
                    action='store',
                    help='the action',
                    dest='action',
                    default=False),
    )
    help = 'valid actions are output which outputs to csv file\n' \
           'more actions....'

    def handle(self, action=None, **options):
        # this will run the code to process the teacher tab from powerschool
        if action == 'output':
            startTime = datetime.now()
            my_format = "%m%d%y%H%M%S"
            error_file = 'master_sch_error_%s.csv' % datetime.now().strftime(my_format)
            my_format2 = "%m_%d_%y_%H%M"
            # set CVS out file files
            csv_output_file = 'csv_output/master_sch/csv_master_sch_%s.csv' % datetime.now().strftime(my_format2)
            csv_header = 'csv_input/master_sch_header.txt'
            #use header_file to fill in csv header from csv_header
            header_file = open(csv_header, 'r')
            csv_header = csv.reader(header_file, delimiter=',', quotechar='"')
            header = csv_header.next()
            header_file.close()
            #open csv outpu file
            outfile = open(csv_output_file, "wb")
            my_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            my_writer.writerow(header)
            school_orange = 2
            school_hs = 1
            school_bethany = 3
            #get all Course from course table except
            master_sch_set = Masterschoolschedule.objects.filter(calendaryearseq=16, schoolprofileseq=school_bethany)

            #go threw each teacher and gather info
            for counter, a_master_sch_item in enumerate(master_sch_set):
                room = ""
                teacher_number = ""
                teacher_name = ""
                print "The Counts is %s of %i" % (counter, len(master_sch_set))
            #"!---Course Number---!"
                course_seq = a_master_sch_item.schoolcourseseq.courseseq
                try:
                    ms_course = Course.objects.get(courseseq=course_seq)
                    course_number = ms_course.coursetitle
                    course_name = ms_course.coursename
                except Course.DoesNotExist:
                    err_code = "This schoolcourseseq  %s with schoolcourseseq %s does not match have a course " \
                               "in the course tablet" % \
                               (a_master_sch_item.schoolcourseseq, a_master_sch_item.schoolcourseseq)
                    write_error(err_code, a_master_sch_item.scheduleseq)
            #"!----Section Number----!
                section_number = a_master_sch_item.coursesectionseq.coursesecdesc
            #"!----TermID----!

            #"!----Teacher Number----!", "!----Teacher Name----!"
                try:
                    teacher = Teacherschedule.objects.get(scheduleseq=a_master_sch_item.scheduleseq)
                    teacher_name = "%s %s " % (
                        teacher.teacherseq.personseq.firstname, teacher.teacherseq.personseq.lastname
                    )
                    try:
                        teacher_number  = Hrsbio.objects.get(personseq=teacher.teacherseq.personseq).altempid
                    except Hrsbio.DoesNotExist:
                        write_error(error_file, "Hrsbio:teacher_altempid", teacher.teacherseq)
                except Teacherschedule.DoesNotExist:
                    err_code = "Teacherschedule does not have a %s" % a_master_sch_item.scheduleseq
                    write_error(error_file, err_code, a_master_sch_item.scheduleseq)
                except Teacherschedule.MultipleObjectsReturned:
                    err_code = "MultipleObjectsReturned for %s scheduleseq in Teacherschedule" % \
                               a_master_sch_item.scheduleseq
                    write_error(error_file, err_code, a_master_sch_item.scheduleseq)
            #"!----Room----!
                try:
                    room = Roomcatalog.objects.get(roomcatalogseq=a_master_sch_item.roomcatalogseq).roomcode
                except Roomcatalog.DoesNotExist:
                    err_code = "Had no rooms for scheduleseq = %s" % a_master_sch_item.scheduleseq
                    write_error(err_code, a_master_sch_item.roomcatalogseq)
                except Roomcatalog.MultipleObjectsReturned:
                    err_code = "This scheduleseq = %s returned multiple entries for rooms" % \
                               a_master_sch_item.scheduleseq
                    write_error(error_file, err_code, a_master_sch_item.roomcatalogseq)

            #"!----Expression ----!" (period and day)
                master_sch_day = Schoolcycle.objects.get(
                    schoolcycleseq=a_master_sch_item.schoolcycleseq
                ).daytitleabbr

                master_sch_period  = Schoolperiods.objects.get(
                    schoolperiodsseq=a_master_sch_item.schoolperiodsseq
                ).periodtitleabbr
                expression = "%s(%s)" % (master_sch_period, master_sch_day)
            # "!----SchoolID----!
                school_id = a_master_sch_item.schoolprofileseq.schoolcode
                school_id = "205%s" % school_id

            #"!---ExcludeFromClassRank---!"
                exclude_from_rank = 0
            #"!---ExcludeFromGPA---!"
                exclude_from_gpa =0
            #"!---ExcludeFromHonorRoll---!"
                exclude_from_honorroll = 0
            #"!---ExcludeFromStoredGrades---!"
                exclude_from_stored_grades = 0
            #"!----MaxEnrollment----!"
                max_entrollment = a_master_sch_item.coursesectionseq.maxseats
            #"!----grade_level----!
                grade_lvl = ''
                try:
                    grade_lvl = Gradelevel.objects.get(gradelevelseq=a_master_sch_item.gradelevelseq).gradelevel
                except Gradelevel.DoesNotExist:
                    err_code = "scheduleseq %s does not have a entry in Gradelevel for gradelevleseq %s" % \
                               (a_master_sch_item.scheduleseq, a_master_sch_item.gradelevelseq)
                    write_error(error_file,err_code, a_master_sch_item.scheduleseq)
            #"!----TermID----!"
                termid = ""
                term_number = ''
                num_of_terms = a_master_sch_item.schoolcourseseq.numofterms
                z_term_number = a_master_sch_item.schooltermseq.schooltermseq
                print school_id
                print num_of_terms
                print "z_term_number = %s" % z_term_number
                if school_id == '2056112':
                    print "High School"
                    print num_of_terms
                    if num_of_terms == 4:
                        term_number = 2300
                    elif z_term_number in(93, 94):
                        term_number = 2301
                    elif z_term_number in (95, 96):
                        term_number = 2302
                    print "term num %s" % term_number
                #orange school 5212
                elif school_id == '2055212':
                    print "orange Middle School"
                    print num_of_terms
                    if num_of_terms == 4:
                        term_number = 2300
                    elif num_of_terms == 1:
                        if z_term_number == 101:
                            term_number = 2303
                        elif z_term_number == 102:
                            term_number = 2304
                        elif z_term_number == 103:
                            term_number = 2305
                        elif z_term_number == 104:
                            term_number = 2306
                    else:
                        if z_term_number in (101, 102):
                            term_number = 2301
                        elif z_term_number in (103, 104):
                            term_number = 2302
                #Bethany school 5112
                elif school_id == '2055112':
                    print "orange Middle School"
                    print num_of_terms
                    if num_of_terms == 4:
                        term_number = 2300
                    elif num_of_terms == 1:
                        if z_term_number == 97:
                            term_number = 2303
                        elif z_term_number == 98:
                            term_number = 2304
                        elif z_term_number == 99:
                            term_number = 2305
                        elif z_term_number == 100:
                            term_number = 2306
                    else:
                        if z_term_number in (97, 98):
                            term_number = 2301
                        elif z_term_number in (99, 100):
                            term_number = 2302
                ipass_termid = "%s_%s" % (z_term_number, num_of_terms)
                my_csv_row = [
                   ipass_termid , course_number, course_name, section_number, term_number,
                    teacher_number, teacher_name, room, expression,
                    "!----Attendance_Type_Code----!", "Att_ModeMeeting", school_id,
                    exclude_from_rank, exclude_from_gpa, exclude_from_honorroll,
                    exclude_from_stored_grades, max_entrollment,a_master_sch_item.scheduleseq, master_sch_day, master_sch_period
                ]

                my_writer.writerow(my_csv_row)
                print(datetime.now()-startTime)
            print(datetime.now()-startTime)