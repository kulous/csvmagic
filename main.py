#!/usr/bin/env python
import sys
import json as JSON


def help(text):
  if text:
    print 'Notice: ' + text
    print '''
help

usage:		{cmd} [-e|-h|-i|-j|-l|-m|-n|-r|-R] file.csv

options
	
  -e			escape special characters
  -f |--file=		specify a csv file to read
  -h 			prints this help text
  -i			print invalid rows
  -j			outputs in json format
  -l | --limit=		specify a line limit to stop reading after x amount of data lines
  -m | --min=		minimum number of matching columns for line to be included
  -n			print line numbers
  -r | --removecolum=	remove column by header name or column position 
  -R | --removerow=	remove all rows that contain regular expression

'''.format(cmd=sys.argv[0])
  sys.exit(1)

def gracefulExit():
  if json:
    print JSON.dumps(j)
  print "# Scanned lines: ",
  print rc
  print "# Requested Limit: ",
  print limit
  print "# Removed Rows: ",
  print removedrows
  if mcount > 0:
    print "# Invalid Rows: ",
    print mcount
  print "# Valid Rows: ",
  print goodrows

  if printinvalid:
    print "Invalid Rows:"
    for i in invalid:
      print "... " + i
  sys.exit(1)

#################
# arguments     #
#################

if len(sys.argv) < 2:
  help('you must specify a file to work with!')

csvfile = sys.argv[len(sys.argv) -1]

import getopt,re


removerow = False
removecolumn = False
json = False
limit = 10000000000
# output options
printcsv = False
printlineno = False
printheaders = True
printnew = True
min=0
printinvalid=False
invalid = []

# stats
mcount = 0
removedrows = 0
goodrows = 0

letters = 'l:r:R:nhjm:i'
keywords = ['limit=','removecolumn=','removerow=','min=']

try:
  opts,extraparams = getopt.getopt(sys.argv[1:],letters,keywords)
except:
  help('invalid options')


for option,value in opts:
  if option in ['-l','--limit']:
    limit = value
  if option in ['-r','--removecolumn']:
    removecolumn = value.strip()
  if option in ['-R','--removerow']:
    removerow = value
  if option in ['-n']:
    printlineno = True
  if option in ['-h']:
    help('showing help text')
  if option in ['-j']:
    json = True
  if option in ['-i']:
    printinvalid = True
  if option in ['-m','--min']:
    min = int(value)

# sanity check required arguments
try:
  csvfile
except:
  help('A CSV file is required')

# to append a field at the beginning of each line, change false -> new static field
injectFirst = False

# replace a static field. this must be a 100% string match for the entier field
replaceField = False

# replace at a specific field location. must be integer
replacePosition = False

# new value to write
replaceValue = "monkeyness"

if json:
  printnew = False
  printlineno = False
  printheaders = False

headers = True

rc = 0
c = 1
j= []

with open(csvfile) as handle:
  data = handle.read()
  for line in data.splitlines():

    if c >  int(limit):
      print "# Exiting at limit of ", limit
      gracefulExit()

    # count each line, including headers, comments and blank lines
    rc += 1

    # process headers
    if rc == 1 and headers:
      headers = line
      hh = []
      for i in line.split(","):
        hh.append(i.strip())
      if printheaders:
        #print "# headers"
        print headers
      continue

    # skip blank lines for performance
    if line == '':
      #print "# skipping blank line"
      continue

    # ignore comments
    if line.startswith("#"):
      print "# ignoring comment"
      invalid.append('COMMENT: ' + line)
      continue


    # clean any whitespace
    line = line.strip()


    # check for first field injection
    if injectFirst:
      line = "{v1},{v2}".format(v1=injectFirst,v2=line)

    # create a csv list
    csv = []
    for i in line.split(","):
      csv.append(i.strip())

    # pad for missing fields
    if headers:
       while len(csv) < len(hh):
         csv.append('')

    # remove column
    if removecolumn:
      try:
        csv.remove(removecolumn)
      except:
        pass

    # remove row TODO THIS NEEDS TO BE A REGULAR EXPRESSION SEARCH
    if removerow:
      matched = False
      for i in csv:
        if re.search(removerow,i):
          matched = True
          continue
      if matched:
        removedrows += 1
        invalid.append('REMOVEROW: ' + line)
        continue 

    # static field replacement
    if replaceField and replaceValue:
      try:
        csv[csv.index(replaceField)] = replaceValue
      except:
        pass

    # require a number of columns to not be empty
    if min > 0:
      validrows = 0
      for i in csv:
        if i != '':
          validrows += 1
      if validrows <  min:
        mcount += 1
        invalid.append('MINIMUMNONEMPTY: ' + line)
        continue
      

    goodrows += 1
    # display and output options below

    if json:
      count = 0
      jr = dict()
      if headers:
        for field in hh:
          jr[field] = csv[count]
          count += 1
        j.append(jr)
          

    if printcsv:
      print csv

    # join the line back together
    line = ",".join(csv)

    if printlineno:
      print c,

    # count as an actual line now
    c += 1


    # print the finished line
    if printnew:
      print line

gracefulExit()

