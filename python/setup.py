import sys

import system_requirements

def check_requirements():
    print('Checking system requirements...')
    result = system_requirements.check()
    print('')

    if(result == system_requirements.State.PASS):
        print('This system meets all requirements.')
    elif(result == system_requirements.State.WARN):
        while(True):
            print('This system may be insufficient, proceed at your own risk. ', end='')
            answer = input('Proceed? [y/n] ')
            if answer.lower() in ["y","yes"]:
                break
            elif answer.lower() in ["n","no"]:
                print('Aborting.')
                sys.exit(1)
    else:
        print('This system does not meet the minimum requirements, aborting.')
        sys.exit(1)

if __name__ == '__main__':
    check_requirements()