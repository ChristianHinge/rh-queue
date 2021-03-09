#/usr/bin/env bash
_complete_functions() {
  if [ ${#COMP_WORDS[@]} -eq 2 ]; then
    COMPREPLY=($(compgen -W "queue remove info" "${COMP_WORDS[1]}"))
  elif ((${#COMP_WORDS[@]} >= 3)); then
    if [ "${COMP_WORDS[-1]:0:2}" == "--" ]; then
      COMPREPLY=($(compgen -W "args conda-venv venv source-script priority email output-file begin-time servers script-name" "${COMP_WORDS[-1]#--}"))
    elif [ "${COMP_WORDS[-1]:0:1}" == "-" ]; then
      COMPREPLY=($(compgen -W "a c v p e o b s" "${COMP_WORDS[-1]#-}"))
    else
      COMPREPLY=($(compgen -o plusdirs -G ${COMP_WORDS[-1]}*.py "${COMP_WORDS[-1]}"))
    fi
  fi

}
complete -F _complete_functions rhqueue
