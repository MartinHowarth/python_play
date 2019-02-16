
_complete_naval()
{
    local cur_word prev_word

    cur_word=${COMP_WORDS[COMP_CWORD]}
    comp_words_trunc=("${COMP_WORDS[@]::${#COMP_WORDS[@]}-1}")


    _0=( "naval" )
    _1=( "naval" "mine" )
    _2=( "naval" "mine" "remove" )
    _3=( "naval" "mine" "set" )
    _4=( "naval" "ship" )
    _5=( "naval" "ship" "move" )
    _6=( "naval" "ship" "new" )
    _7=( "naval" "ship" "shoot" )

    if [[ 0 == 1 ]] ;
    then
        COMPREPLY=()

    elif [[ ${_0[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "mine ship" -- ${cur_word}))
    elif [[ ${_1[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "remove set" -- ${cur_word}))
    elif [[ ${_2[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "" -- ${cur_word}))
    elif [[ ${_3[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "" -- ${cur_word}))
    elif [[ ${_4[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "move new shoot" -- ${cur_word}))
    elif [[ ${_5[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "" -- ${cur_word}))
    elif [[ ${_6[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "" -- ${cur_word}))
    elif [[ ${_7[@]} == ${comp_words_trunc[@]} ]] ;
    then
        COMPREPLY=($(compgen -W "" -- ${cur_word}))
    else
        COMPREPLY=()
    fi

}

complete -o nosort -F _complete_naval naval
