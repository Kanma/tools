#! /usr/bin/env python

from optparse import OptionParser
import sys
import os


################################### FUNCTIONS ##################################

def process(options, path, files):
    for file in filter(lambda x: os.path.splitext(x)[1] in options.extensions, files):

        # Open the file
        fullpath = os.path.join(path, file)
        f = open(fullpath, "r")
        original_content = f.read()
        f.close()

        # Remove the EOL sequence
        if options.eol_sequence == 'crlf':
            eol = '\r\n'
            content = original_content
            offset = content.find('\r')
            while offset >= 0:
                if content[offset + 1] != '\n':
                    content = content[0:offset] + '\r\n' + content[offset+1:] 
                offset = content.find('\r', offset + 1)
            content = content.replace('\n', eol)
        elif options.eol_sequence == 'cr':
            eol = '\r'
            content = original_content.replace('\r\n', eol).replace('\n', eol)
        else:
            eol = '\n'
            content = original_content.replace('\r\n', eol).replace('\r', eol)

        modified = (content != original_content)

        lines = []
        for line in content.split(eol):
            # Remove the trailing spaces and tabs
            line2 = line.rstrip()

            # Replace the tabs by spaces, keeping the current alignement
            offset = line2.find('\t')
            while offset >= 0:
                real_offset = (offset // options.tab_size) * options.tab_size
                line2 = line2[0:offset] + ' ' * (options.tab_size - (offset - real_offset)) + line2[offset+1:] 
                offset = line2.find('\t')

            lines.append(line2)

            modified = modified or (line2 != line)

        # Add an empty line at the end if necessary
        if (len(lines) > 0) and (len(lines[-1]) > 0):
            modified = True
            lines.append('')

        if modified:
            # Save a backup of the file
            backup = open(fullpath + '~', "w")
            backup.write(original_content)
            backup.close()

            # Save the processed file
            result = open(fullpath, "w")
            result.write(eol.join(lines))
            result.close()

            print("MODIFIED: %s" % fullpath[len(options.rootdir)+1:])
            options.counter += 1 



##################################### MAIN #####################################

if __name__ == "__main__":

    # Setup of the command-line arguments parser
    usage = """Usage: %prog [options] [ext1] [ext2] [...]

Apply the following transformations to all the files with the
given extension(s) in the current folder (and below):

  - Replace TAB characters with spaces, keeping the current
    alignement
  - Remove trailing spaces at the end of lines
  - Ensure that all lines ends with the same EOL sequence
  - Ensure that the file ends with an empty line

Extensions are given in the form:
  .cpp .h .txt (no asterisk at the beginning)

Copyright (c) 2012 by Philip Abbet
Any use, commercial or not, is allowed
"""

    parser = OptionParser(usage, version="%prog 1.0")
    parser.add_option("-t", action="store", default=4, type="int",
                      dest="tab_size", metavar="TAB_SIZE",
                      help="Number of spaces per TABs (default: 4)")
    parser.add_option("-e", action="store", default="lf", type="string",
                      dest="eol_sequence", metavar="EOL_SEQUENCE",
                      help="The EOL sequence to set: 'lf' (the default), 'cr' or 'crlf'")

    # Handling of the arguments
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print("ERROR: No extension provided\n")
        parser.print_help()
        sys.exit(1)

    options.extensions = args
    options.counter = 0

    # Process the files in the current directory
    options.rootdir = os.getcwd()
    for root, dirs, files in os.walk(options.rootdir):
        process(options, root, files)

    if options.counter > 0:
        print

    if options.counter > 1:
        print("Done (%d files modified)!" % options.counter)
    else:
        print("Done (%d file modified)!" % options.counter)
