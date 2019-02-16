_complete_naval()
{
    local cur prev

    arr=("naval" "ship" "")
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}

#    echo "arr ${arr[@]}"
#    echo "comp ${COMP_WORDS[@]}"
    if [[ ${arr[@]} == ${COMP_WORDS[@]} ]] ;
    then
        echo "yes"
    fi

    case ${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "mine ship" -- ${cur}))
            ;;
        2)
            case ${prev} in
                ship)
                    COMPREPLY=($(compgen -W "move new shoot" -- ${cur}))
                    ;;
                mine)
                    COMPREPLY=($(compgen -W "remove set" -- ${cur}))
                    ;;
            esac
            ;;
        3)
            case ${prev} in
                move)
                    if [[ ${cur} == -* ]] ;
                    then
                        COMPREPLY=($(compgen -W "--speed --help" -- ${cur}))
                    fi
                    ;;
            esac
            ;;
         *)
            COMPREPLY=()
            ;;
    esac
}

complete -o nosort -F _complete_naval naval