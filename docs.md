= RHQueue =
This script is for queueing and canceclling scripts to be run on the titan servers
It's usage is <code>rhqueue queue <args> <script></code> or <code>rhqueue remove <job_id></code>.
The args for <code>rhqueue queue</code> are:
= Queue =
== Usage ==
    
    <code>rhqueue queue [-h] [-v venv | -c condaVenv] [-p {1,2,3,4,5}] [-e EMAIL]
                     [-o OUTPUT_FILE] [-b BEGIN_TIME] [-t TITAN [TITAN ...]]
                     [-a ARGS [ARGS ...]] [--test]
                     script</code>

== Positional Arguments ==

=== Script ===
''' Usage '''
<code>rhqueue queue <script></code>

''' Description '''
The script to run on a gpu. At the top of each file there must be the shebang 
<code>#!/usr/bin/env <python_version></code>. Where <code><python_version></code> 
is the version of python needed, python(for 2.7) or python3

''' Examples '''
command-line: <code>rhqueue queue <script></code>

shebang: <code>#!/usr/bin/env python3</code>

== Optional Arguments ==

=== Virtual Environment ===
''' Usage '''
<code>-v <venv>, --venv <venv></code>

''' Description '''
The virtual environment used for the project. The value is the absolute path to the virtual environment directoy

''' Example '''
<code>rhqueue queue -v /homes/pmcd/venv/test-venv script.py</code>

=== Conda Environment ===
''' Usage ''' 
<code>-c condaVenv, --conda-venv condaVenv </code>

''' Description '''
The environment for conda. This is supposed to be the name of the conda environment.

''' Example '''
<code>rhqueue queue -c test-conda script.py</code>


=== Priority ===
''' Usage '''
<code>-p {1,2,3,4,5}, --priority {1,2,3,4,5}</code>

''' Description '''
The priority of the script DO NOT DEFINE UNLESS YOU ARE SURE THAT YOU DO NOT NEED HIGHER PRIORITY.

''' Example '''
<code>rhqueue queue -p 4 script.py</code>


=== Email ===
''' Usage '''
<code>-e EMAIL, --email EMAIL</code>

''' Description '''
The email to send to when the script begins and ends. Can be defined as environment variable (<code>export RHQ_EMAIL=<email></code>) to use as a default. This will prefer the email given in the argument line over the environtment variable

''' Example '''
<code>rhqueue queue --email pjens.jensen@regionhdk script.py</code>


=== Output File ===
''' Usage '''
<code>-o OUTPUT_FILE, --output-file OUTPUT_FILE</code>

''' Argument Type '''
<code>OUTPUT_FILE</code> is a path to the location of the file is relative to where the script is run

''' Description '''
The file for the output of the script. This is the path to the file. Default is 'my.stdout'

''' Example '''
<code>rhqueue queue -o test.stdout script.py</code>


=== Begin Time ===
''' Usage '''
<code>-b BEGIN_TIME, --begin-time BEGIN_TIME</code>

''' Description '''
Begin script after (<code>b</code>) seconds

''' Example '''
<code>rhqueue queue -b 60 script.py</code>
The begin time will be earliest 60 seconds after the script is queued


=== Titans ===
''' Usage '''
<code>-t TITAN [TITAN ...], --titan TITAN [TITAN ...]</code>

''' Description '''
Define the titans that the script can run on. The script will run on the first available of the titans selected.

''' Example '''
<code>rhqueue queue -t 1 2 3 script.py</code>

Will run the script on any of titan 1,2, or 3


=== Script Arguments ===
''' Usage '''
<code>-a ARGS [ARGS ...], --args ARGS [ARGS ...]</code>

''' Description '''
The arguments for the script. These are passed to the script to run. Pass these in the same method as you would normally

''' Example '''
<code>rhqueue queue sum.py --args 1 2 3 4 5</code>


=== Test Script ===
''' Usage '''
<code>--test</code>

''' Description '''
Desclares that the script is a test. This will not queue the script

''' Example '''
<code>rhqueue queue --test script.py</code>

== Full Examples ==
* <code>rhqueue queue -t 1,2,3 -v /homes/pmcd/venv/test-venv -e jens.jensen@regionh.dk sum.py --args 1 2 3 4 5</code>
** This will queue the script <code>sum.py</code> with the virtual environtment <code>test-slurm</code>, run on one of the titans 1, 2, or 3, with the arguments 1,2,3,4 and 5, while sending an email to <code>jens.jensen@regionh.dk</code>

= Remove =
The rhqueue also allows for the removal or cancellation of a queued script.

== Usage ==
<code>rhqueue remove [-h] job</code>

== Positional Arguments ==

=== Job ===

''' Description '''
The id of the job to cancel can be found by using <code>rhqueue info</code>

'''Usage'''
<code>rhqueue remove <job_id></code>

'''Example '''
<code>rhqueue remove 123</code>

= Info =
This argument is used to look at the queue of scripts

== Usage ==
<code>rhqueue info [-h]</code>

''' Example '''
<code>rhqueue info</code>