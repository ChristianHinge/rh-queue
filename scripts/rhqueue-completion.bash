#/usr/bin/env bash
_complete_rhqueue() {
    local cur=$2;
    local prev=$3;
    if [ ${#COMP_WORDS[@]} -eq 2 ]; then
        COMPREPLY=($(compgen -W "queue remove info" "${COMP_WORDS[1]}"))
    elif ((${#COMP_WORDS[@]} >= 3)); then
        # case 
        case "${COMP_WORDS[1]}" in
            queue)
                if [ "${cur:0:2}" == "--" ]; then
                    COMPREPLY=($(compgen -P '--' -W "args conda-venv venv source-script priority email output-file begin-time servers script-name help" "${cur:2}"))
                elif [ "${cur:0:1}" == "-" ]; then
                    COMPREPLY=($(compgen -P '-' -W "a c v p e o b s h" "${cur:1}"))
                elif [[ "$prev" == "-v" || "$prev" == "--venv" ]]; then
                    if [[ "$RHQ_VENV_LOCATIONS" == "" ]]; then
                        COMPREPLY=()
                    else
                        COMPREPLY=($(compgen -P "$RHQ_VENV_LOCATIONS/" -W "$(ls $RHQ_VENV_LOCATIONS/)" "$cur"))
                    fi
                elif [[ "$prev" == "-c" || "$prev" == "--conda-venv" ]]; then
                    if [[ "$RHQ_CONDALOC" == "" ]]; then
                        COMPREPLY=()
                    else
                        COMPREPLY=($(compgen -W "$(ls $RHQ_CONDALOC/envs/)" "$cur"))
                    fi
                elif [[ "$prev" == "--source-script" ]]; then
                    COMPREPLY=($(compgen -o plusdirs -f -X '!*.*' --  "$cur"))
                else
                    local IFS=$'\n'
                    COMPREPLY=($(compgen -o plusdirs -f -X '!*.py' -- "$cur"))
                fi
                ;;
            info)
                if [[ "${cur:0:2}" == "--" ]]; then
                    COMPREPLY=($(compgen -P '--' -W "help verbose job-id" -- "${cur:2}"))
                elif [[ "${cur:0:1}" == "-" ]]; then
                    COMPREPLY=($(compgen -P '-' -W "j v h" -- "${cur:1}"))
                elif [[ "$prev" == "-j" || "$prev" == "--job-id" ]]; then
                    COMPREPLY=($(compgen -W "$(squeue -o '%A' -h | tr '\n' ' ')" -- "$cur"))
                fi
                ;;
            remove)
                COMPREPLY=($(compgen -W "$(squeue -o '%A' -h | tr '\n' ' ')" -- "$cur"))
                ;;
        esac
    fi
}
complete -o filenames -F _complete_rhqueue rhqueue