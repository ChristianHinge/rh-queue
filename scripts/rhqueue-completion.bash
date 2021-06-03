#/usr/bin/env bash
_complete_rhqueue() {
    local cur=${COMP_WORDS[-1]};
    local prev=${COMP_WORDS[-2]};
    if [ ${#COMP_WORDS[@]} -eq 2 ]; then
        COMPREPLY=($(compgen -W "queue remove info" "${COMP_WORDS[1]}"))
    elif ((${#COMP_WORDS[@]} >= 3)); then
        # case 
        case "${COMP_WORDS[1]}" in
            queue)
                if [ "${cur:0:2}" == "--" ]; then
                    COMPREPLY=($(compgen -P '--' -W "args conda-venv venv source-script priority email output-file begin-time servers script-name" "${cur:2}"))
                elif [ "${cur:0:1}" == "-" ]; then
                    COMPREPLY=($(compgen -P '-' -W "a c v p e o b s" "${cur:1}"))
                elif [[ "$prev" == "-v" || "$prev" == "--venv" ]]; then
                    COMPREPLY=($(compgen -W "$(ls $RHQ_VENV_LOCATIONS/)" "${cur}"))
                elif [[ "$prev" == "-c" || "$prev" == "--conda-venv" ]]; then
                    COMPREPLY=($(compgen -W "$(ls $RHQ_CONDALOC/envs/)" "${cur}"))
                else
                    local IFS=$'\n'
                    COMPREPLY=($(compgen -o plusdirs -f -X '!*.py' -- "${cur}"))
                fi
                ;;
            info)
                if [ "${cur:0:1}" == "-" ]; then
                    COMPREPLY=($(compgen -W "-j -v" -- "${cur}"))
                elif [ "$prev" == "-j" ]; then
                    COMPREPLY=($(compgen -W "$(squeue -o '%A' -h | tr '\n' ' ')" -- "${cur}"))
                fi
                ;;
            remove)
                COMPREPLY=($(compgen -W "$(squeue -o '%A' -h | tr '\n' ' ')" -- "${cur}"))
                ;;
        esac
    fi
}
complete -o filenames -F _complete_rhqueue rhqueue