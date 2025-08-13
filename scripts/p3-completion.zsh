# zsh completion for p3 (scoped to my_finance)

_p3_commands=(pr e2e refresh clean)
_p3_scopes=(f2 m7 n100 v3k)

_p3() {
  local -a cmds scopes
  cmds=(${_p3_commands})
  scopes=(${_p3_scopes})

  if (( CURRENT == 2 )); then
    compadd -x '提示        说明'
    compadd -x 'pr          创建/更新 PR（带校验）。例: p3 pr "修复" 81'
    compadd -x 'e2e         端到端校验（不创建 PR）。例: p3 e2e'
    compadd -x 'refresh     构建数据（默认 m7）。例: p3 refresh m7'
    compadd -x 'clean       清理本地构建产物。例: p3 clean'
    compadd -x 'f2          快速 2 公司（开发）。例: p3 refresh f2'
    compadd -x 'm7          Magnificent 7（默认/PR）。例: p3 refresh m7'
    compadd -x 'n100        NASDAQ100（验证）。例: p3 refresh n100'
    compadd -x 'v3k         VTI 3500+（生产）。例: p3 refresh v3k'
    compadd -a cmds
    return
  fi

  local cmd=$words[2]
  case $cmd in
    refresh)
      if (( CURRENT == 3 )); then
        compadd -x '提示   说明'
        compadd -x 'f2     快速 2 公司（开发）。例: p3 refresh f2'
        compadd -x 'm7     Magnificent 7（默认/PR）。例: p3 refresh m7'
        compadd -x 'n100   NASDAQ100（验证）。例: p3 refresh n100'
        compadd -x 'v3k    VTI 3500+（生产）。例: p3 refresh v3k'
        compadd -a scopes
        return
      fi
      ;;
  esac
}

compdef -P _p3 **/my_finance/p3 p3


