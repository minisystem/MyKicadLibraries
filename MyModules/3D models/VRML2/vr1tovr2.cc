/*
   Copyright (c) 2007, Roger Kaufman

   Permission is hereby granted, free of charge, to any person obtaining a
   copy of this software and associated documentation files (the "Software"),
   to deal in the Software without restriction, including without limitation
   the rights to use, copy, modify, merge, publish, distribute, sublicense,
   and/or sell copies of the Software, and to permit persons to whom the
   Software is furnished to do so, subject to the following conditions:

      The above copyright notice and this permission notice shall be included
      in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
  IN THE SOFTWARE.
*/

/*
   Name: vr1tovr2.cc
   Description: Wrapper to give vrml1tovrml2.exe stdin and stdout support
   Project: Antiprism - http://www.antiprism.com
*/


#include <stdio.h>
#include <stdlib.h>

#include <ctype.h>
#include <unistd.h>

#include <string>
#include <vector>

#include "../base/antiprism.h"

using std::string;
using std::vector;

#define COMMAND_SIZE 512

class oang_opts: public prog_opts {
   public:
      string ifile;
      string ofile;

      oang_opts(): prog_opts("vr1tovr2")
             {}

      void process_command_line(int argc, char **argv);
      void usage();
};



void oang_opts::usage()
{
   fprintf(stderr,
"\n"
"Usage: %s [options] [input_file]\n"
"\n"
"Convert vrml1 to vrml2 via vrml1tovrml2.exe (external program). If\n"
"input_file is not given the program reads from standard input.\n"
"\n"
"Options\n"
"  -h        this help message\n"
"  -o <file> file name for output (otherwise prints to stdout)\n"
"\n"
"\n", prog_name());
}


void oang_opts::process_command_line(int argc, char **argv)
{
   extern char *optarg;
   extern int optind, opterr, optopt;
   opterr = 0;
   char c;
//   char errmsg[MSG_SZ];
   
   while( (c = getopt(argc, argv, ":ho:")) != -1 ) {
      switch(c) {
         case 'h':
            usage();
            exit(0);

         case 'o':
            ofile = optarg;
            break;

         case '?':
            error("unknown option", string("-")+(char)optopt);

         case ':':
            error("missing argument", string("-")+(char)optopt);

         default:
            error("unknown command line error");
      }
   }

   if(argc-optind > 1)
      error("too many arguments");
   
   if(argc-optind == 1)
      ifile=argv[optind];

}

vector<string> read_file_to_mem(string file_name, char *errmsg)
{
   string str;
   vector<string> buf;

   if(errmsg)
      *errmsg='\0';

   FILE *ifile;
   if(file_name == "" || file_name == "-") {
      ifile = stdin;
      file_name = "stdin";
   }
   else {
      ifile = fopen(file_name.c_str(), "r");
      if(!ifile) {
         if(errmsg)
            snprintf(errmsg, MSG_SZ, "could not open input file \'%s\'", file_name.c_str());
         return buf;
      }
   }

   char *line=0;
   while(read_line(ifile, &line)==0) {
      buf.push_back(line);
      free(line);
   }
   
   if(file_name!="stdin")
      fclose(ifile);

   return buf;
}

void write_mem_to_file(string file_name, vector<string> *memfile,  char *errmsg)
{
   FILE *ofile;
   if(file_name == "" || file_name == "-") {
      ofile = stdout;
      file_name = "stdout";
   }
   else {
      ofile = fopen(file_name.c_str(), "w");
      if(!ofile) {
         if(errmsg)
            snprintf(errmsg, MSG_SZ, "could not open output file \'%s\'", file_name.c_str());
      }
   }

   // create temporary input file
   for(unsigned int i=0;i<memfile->size();i++)
      fprintf(ofile,"%s\n",(*memfile)[i].c_str());

   if(file_name!="stdout")
      fclose(ofile);
}

int main(int argc, char *argv[])
{
   oang_opts opts;
   opts.process_command_line(argc, argv);

   char errmsg[MSG_SZ];

   // read vrmltxt into array
   vector<string> vrmltxt;
   vrmltxt = read_file_to_mem(opts.ifile, errmsg);
   if(*errmsg)
      opts.error(errmsg);

   // check ahead of time to see if file is valid
   if ( vrmltxt[0].compare("#VRML V1.0 ascii") )
      opts.error("Input file does not appear to be vrml 1.0");

   // write out tmp file for vrml1tovrml2
   char *tmpname1;
   if( ( tmpname1 = _tempnam( NULL, "wrl1-" ) ) == NULL )
      opts.error("Cannot create a unique filename");
   else {
      write_mem_to_file(tmpname1, &vrmltxt, errmsg);
      if(*errmsg)
         opts.error(errmsg);
   }

   vrmltxt.clear();

   char *tmpname2;
   if( ( tmpname2 = _tempnam( NULL, "wrl2-" ) ) == NULL )
      opts.error("Cannot create a unique filename");

   char command[COMMAND_SIZE];
   snprintf(command,COMMAND_SIZE,"vrml1tovrml2 %s %s", tmpname1, tmpname2);
   system(command);

   remove(tmpname1);

   // read temporary result into array
   vrmltxt = read_file_to_mem(tmpname2, errmsg);
   if(*errmsg) {
      opts.warning("Can vrml1tovrml2.exe be found in your system path?");
      opts.error(errmsg);
   }
   else {
      // The attribute of output file becomes read only within vrml1tovrml2. undo that.
      snprintf(command,COMMAND_SIZE,"attrib -r %s", tmpname2);
      system(command);

      remove(tmpname2);
   }

   // So the the output file can always be written
   if(opts.ofile != "") {
      // if the output file is read only from previous run of vrml1tovrml2, undo that.
      snprintf(command,COMMAND_SIZE,"attrib -r %s", opts.ofile.c_str());
      system(command);
   }

   // write out result from vrml1tovrml2
   write_mem_to_file(opts.ofile, &vrmltxt, errmsg);
   if(*errmsg)
         opts.error(errmsg);

   vrmltxt.clear();

   return 0;
}
