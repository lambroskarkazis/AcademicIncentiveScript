import sys
import unittest
import csv
import math

class IGetPoints:
    def getPoints(self):
        return 0

class StudySession(IGetPoints):
    def __init__(self, numHours):
        self.hours = numHours

    def __str__(self):
        return str(self.hours)

    def getPoints(self):
        return self.hours

class DigitalStudyResources(IGetPoints):
    def __init__(self, numFiles):
        self.numFiles = numFiles

    def getPoints(self):
        return numFiles

class PhysicalStudyResources(DigitalStudyResources):
    def getPoints(self):
        return .25 * self.numFiles

class ProfessorOfficeHours(IGetPoints):
    def getPoints(self):
        return 3

class CourseReviews(IGetPoints):
    def __init__(self, numCourseReviews):
        self.numCourseReviews = numCourseReviews

    def getPoints(self):
        return self.numCourseReviews * .5

class Planner(IGetPoints):
    def getPoints(self):
        return 10

    def __init__(self):
        self.numPlanners = 1

class Student(IGetPoints):
    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName
        self.activities = []
        self.requiresHours = False
        self.gpa = None
        self.oldGpa = None

    def __str__(self):
        return self.getFirstName() + ' ' + self.getLastName()

    def __eq__(self, other):
        return self.firstName == other.firstName and self.lastName == other.lastName

    def getFirstName(self):
        return self.firstName

    def getLastName(self):
        return self.lastName

    def addEvent(self, scholarshipEvent):
        self.activities.append(scholarshipEvent)

    def setRequiresHours(self, requiresHours):
        self.requiresHours = requiresHours

    def getRequiredHours(self):
        if self.requiresHours:
            return 26
        else:
            return 0

    def getPoints(self):
        return math.fsum( [event.getPoints() for event in self.activities] ) - self.getRequiredHours()

    def getGpa(self):
        return self.gpa

    def setGpa(self, gpa):
        self.gpa = gpa

    def getOldGpa(self):
        return self.oldGpa

    def setOldGpa(self, oldGpa):
        self.oldGpa = oldGpa

    def getGpaImprovement(self):
        if self.getGpa() is not None and self.getOldGpa() is not None:
            return self.getGpa() - self.getOldGpa()
        return None

class Team(IGetPoints):
    def __init__(self, teamName):
        self.teamName = teamName
        self.members = []

    def __str__(self):
        return self.teamName + ' : '+ ', '.join(str(x) for x in self.members)

    def __lt__(self, other):
        return self.getPointsPerMember() > other.getPointsPerMember()

    def addMember(self, teamMember):
        self.members.append(teamMember)
        return self

    def getStudent(self, student):
        if student in self.members:
            index = self.members.index(student)
            return self.members[index]
        else:
            return

    def addMembers(self, listOfTeamMembers):
        self.members.extend(listOfTeamMembers)
        return self

    def removeMember(self, teamMember):
        self.members.remove(teamMember)

    def getPoints(self):
        return math.fsum( [member.getPoints() for member in self.members] )

    def getPointsPerMember(self):
        return self.getPoints() / len(self.members)

    def getTeamName(self):
        return self.teamName

    def getTeamMembers(self):
        return self.members

    def getTeamGpa(self):
        return mean(map(lambda student: student.getGpa(), self.getTeamMembers()))

    def getTeamGpaImprovement(self):
        return mean(map(lambda student: student.getGpaImprovement(), self.getTeamMembers()))
    
    def getSize(self):
        return self.members.count

def calculateFinalTeams(teams):
    gpaRanking = sorted(teams, key = lambda team : team.getTeamGpa())
    pointsRanking = sorted(teams, key = lambda team : team.getPointsPerMember())

    return map(lambda team: (team, gpaRanking.index(team) * 2 + pointsRanking.index(team)), teams)



def parseTeams(fileName):
    teams = []

    with open(fileName, 'rb') as file:
        reader = csv.reader(file)

        members = []
        teamName = 'sample'

        for row in reader:
            if(row[0].strip() == ('')):
                teams.append(Team(teamName).addMembers(members))
                members = []
            elif(row[0][0:4] == ('Team')):
                teamName = row[0].strip()
            else:
                members.append(Student(row[0].strip(), row[1].strip()))

        teams.append(Team(teamName).addMembers(members))
    return teams



def getStudentOnTeam(teams, student):  
    for team in teams:
        foundStudent = team.getStudent(student)
        if foundStudent != None:
          return foundStudent

def getTeamFromStudent(teams, student):
    for team in teams:
        foundStudent = team.getStudent(student)
        if foundStudent != None:
            return team

def parseStudyHours(fileName, teams):
     with open(fileName, 'rb') as file:
        reader = csv.reader(file)
        requiresHours = False

        for row in reader:
            if row[0].strip() != '' and row[1].strip() != '' and row[0][0] != '#':
                student = Student(row[0].strip(), row[1].strip())
                studyHoursObject = StudySession(float(row[2]))
                teamMember = getStudentOnTeam(teams, student)
                if teamMember is not None:
                    teamMember.addEvent(studyHoursObject)
                    teamMember.setRequiresHours(requiresHours)
                else:
                    print str(student) + ' could not be found'
            elif row[0].strip() == 'New Members':
                requiresHours = True
            elif row[0].strip() == 'Probationers':
                requiresHours = True
            elif row[0].strip() == 'Actives':
                requiresHours = False

def parsePlannerSheet(fileName, teams):
    with open(fileName, 'rb') as file:
        reader = csv.reader(file)

        for row in reader:
            if(row[1] != '' and row[2] != ''):
                plannerStudent = Student(row[0].strip(), row[1].strip())
                plannerEvent = Planner()
                recordActivity(teams, plannerStudent, plannerEvent)

def parseOfficeHours(fileName, teams):
    with open(fileName, 'rb') as file:
        reader = csv.reader(file)

        rows = iter(reader)
        next(rows)
        for row in rows:
            student = Student(row[1].strip(), row[2].strip())
            officeHoursEvent = ProfessorOfficeHours()
            recordActivity(teams, student, officeHoursEvent)

def parseCourseReviews(fileName, teams):
    with open(fileName, 'rb') as file:
        reader = csv.reader(file)

        rows = iter(reader)
        next(rows)
        for row in rows:
            student = Student(row[1].strip(), row[2].strip())
            courseReviewsEvent = CourseReviews(float(row[3].strip()))
            recordActivity(teams, student, courseReviewsEvent)

def parseStudyResources(fileName, teams):
    with open(fileName, 'rb') as file:
        reader = csv.reader(file)

        rows = iter(reader)
        next(rows)
        for row in rows:
            student = Student(row[1].strip(), row[2].strip())
            if float(row[3]) > 0:
                physicalStudyResources = PhysicalStudyResources(float(row[3].strip()))
                recordActivity(teams, student, physicalStudyResources)
            if float(row[4]) > 0:
                digitalStudyResources = DigitalStudyResources(float(row[3].strip()))
                recordActivity(teams, student, physicalStudyResources)   
                

def parseEndingGpa(fileName, teams):
    parseGpa(fileName, teams, False)


def parseStartingGpa(fileName, teams):
    parseGpa(fileName, teams, True)


def parseGpa(fileName, teams, isOld):
    with open(fileName, 'rb') as file:
        reader = csv.reader(file)

        rows = iter(reader)
        next(rows)
        for row in rows:
            if row[0].strip() != 'First':
                student = Student(row[0].strip(), row[1].strip())
                if row[3] != '':
                    gpa = float(row[3])
                else:
                    gpa = None
                teamMember = getStudentOnTeam(teams, student)

                if teamMember is not None:
                    if isOld:
                        teamMember.setOldGpa(gpa)
                    else:
                        teamMember.setGpa(gpa)
                else:
                    print str(student) + ' had a GPA but not a team'
                

def recordActivity(teams, student, activity):
    foundStudent = getStudentOnTeam(teams, student)
    if foundStudent is not None:
        foundStudent.addEvent(activity)
    else:
        print str(student) + ' could not be found in list of teams'

def mean(numbers):
    total = 0
    size = 0

    for number in numbers:
        if number is not None:
            total += number
            size += 1

    return total / size
      

teamFileName = 'Spring 2017 Draft - Teams.csv'
studyHoursFileName = 'Study Hours - Spring 2017 - Total Study Hours.csv'
plannerFileName = 'Planner Incentive Log - Sheet1.csv'
officeHoursFileName = 'Professor Office Hours (Responses) - Form Responses 1.csv'
courseReviewsFileName = 'Course Review Incentive Form (Responses) - Form Responses 1.csv'
studyResourcesFileName = 'Study Resources Incentive Form (Responses) - Form Responses 1.csv'
endingGpa = 'Spring 2017 Grades - Grades.csv'
beginningGpa = 'Fall 2016 Grades - Grades.csv'

teams = parseTeams(teamFileName)
parseStudyHours(studyHoursFileName, teams)
parsePlannerSheet(plannerFileName, teams)
parseOfficeHours(officeHoursFileName, teams)
parseCourseReviews(courseReviewsFileName, teams)
parseStudyResources(studyResourcesFileName, teams)
parseEndingGpa(endingGpa, teams)
parseStartingGpa(beginningGpa, teams)

teams.sort()
print('Points Rankings\n')
print('\n'.join(str(team.getPointsPerMember()) + ' points per member ' +  str(team) for team in teams))

print '\n\n\n'

print('GPA Rankings\n')
teams = sorted(teams, key = lambda team : -team.getTeamGpa())
print('\n'.join(str(team.getTeamGpa()) + ' GPA ' + str(team) for team in teams))

print '\n\n\n'

print('GPA Improvement Rankings\n')
teams = sorted(teams, key = lambda team : -team.getTeamGpaImprovement())
print('\n'.join(str(team.getTeamGpaImprovement()) + ' GPA Improvement ' + str(team) for team in teams))

print '\n\n\n'

results = calculateFinalTeams(teams)
results = sorted(results, key = lambda result : -result[1])

print '\n\n\n'
print('Overall Rankings\n')
print('\n'.join(str(result[1]) + ' overall points | ' + str(result[0]) for result in results))
