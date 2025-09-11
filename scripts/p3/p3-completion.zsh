# zsh completion for p3 (simplified 8-command system)

_p3_commands=(ready stop reset check test ship build version)
_p3_scopes=(f2 m7 n100 v3k)

_p3() {
  local -a cmds scopes
  cmds=(${_p3_commands})
  scopes=(${_p3_scopes})

  if (( CURRENT == 2 )); then
    compadd -x 'Command       Description'
    compadd -x 'ready         Start working (env + services)'
    compadd -x 'stop          Stop working (release resources)'
    compadd -x 'check [scope] Validate code (format + lint + test)'
    compadd -x 'test [scope]  Comprehensive testing (e2e validation)'
    compadd -x 'ship          Publish work (test + PR + cleanup)'
    compadd -x 'reset         Fix environment (clean restart)'
    compadd -x 'build [scope] Build dataset (f2/m7/n100/v3k)'
    compadd -x 'version       Show/increment version'
    compadd -a cmds
    return
  fi

  local cmd=$words[2]
  case $cmd in
    check|test|build)
      if (( CURRENT == 3 )); then
        compadd -x 'Scope  Description'
        compadd -x 'f2     Fast 2 companies (development)'
        compadd -x 'm7     Magnificent 7 (standard PR testing)'
        compadd -x 'n100   NASDAQ 100 (validation testing)'
        compadd -x 'v3k    VTI 3500+ (production)'
        compadd -a scopes
      fi
      ;;
    stop)
      if (( CURRENT == 3 )); then
        compadd -x 'Option Description'
        compadd -x '--full Stop Podman machine (complete shutdown)'
        compadd -x '--force Force stop without graceful shutdown'
        compadd "--full" "--force"
      fi
      ;;
    version)
      if (( CURRENT == 3 )); then
        compadd -x 'Level   Description'
        compadd -x 'patch   Increment patch version (x.x.X)'
        compadd -x 'minor   Increment minor version (x.X.x)'
        compadd -x 'major   Increment major version (X.x.x)'
        compadd "patch" "minor" "major"
      fi
      ;;
  esac
}

compdef _p3 p3