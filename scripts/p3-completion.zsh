# zsh completion for p3 (scoped to my_finance)

_p3_commands=(env podman neo4j format lint typecheck test e2e build fast-build refresh create-build release-build clean build-status create-pr commit-data-changes cleanup-branches shutdown-all status cache-status verify-env check-integrity)
_p3_env_commands=(setup start stop status reset)
_p3_podman_commands=(status)
_p3_neo4j_commands=(logs connect restart stop start)
_p3_scopes=(f2 m7 n100 v3k)

_p3() {
  local -a cmds env_cmds podman_cmds neo4j_cmds scopes
  cmds=(${_p3_commands})
  env_cmds=(${_p3_env_commands})
  podman_cmds=(${_p3_podman_commands})
  neo4j_cmds=(${_p3_neo4j_commands})
  scopes=(${_p3_scopes})

  if (( CURRENT == 2 )); then
    compadd -x 'Command     Description'
    compadd -x 'env         Environment management (setup/start/stop/status/reset)'
    compadd -x 'podman      Container management (status)'
    compadd -x 'neo4j       Neo4j management (logs/connect/restart/stop/start)'
    compadd -x 'format      Format code (black + isort)'
    compadd -x 'lint        Lint code (pylint)'
    compadd -x 'typecheck   Type check with mypy'
    compadd -x 'test        Run tests (pytest)'
    compadd -x 'e2e         End-to-end validation [scope]'
    compadd -x 'build       Build dataset (build run [scope])'
    compadd -x 'fast-build  Fast build with deepseek-r1:1.5b [scope]'
    compadd -x 'refresh     Build dataset (alias for build run)'
    compadd -x 'create-pr   Create/update PR with testing'
    compadd -x 'clean       Clean build artifacts'
    compadd -x 'status      Quick environment status'
    compadd -x 'verify-env  Verify environment dependencies'
    compadd -x 'check-integrity  Check data integrity'
    compadd -a cmds
    return
  fi

  local cmd=$words[2]
  case $cmd in
    env)
      if (( CURRENT == 3 )); then
        compadd -x 'Env Command Description'
        compadd -x 'setup       Initial environment setup'
        compadd -x 'start       Start all services'
        compadd -x 'stop        Stop all services'
        compadd -x 'status      Check environment status'
        compadd -x 'reset       Reset everything (destructive)'
        compadd -a env_cmds
      fi
      ;;
    podman)
      if (( CURRENT == 3 )); then
        compadd -a podman_cmds
      fi
      ;;
    neo4j)
      if (( CURRENT == 3 )); then
        compadd -x 'Neo4j Cmd   Description'
        compadd -x 'logs        View Neo4j logs'
        compadd -x 'connect     Connect to Neo4j shell'
        compadd -x 'restart     Restart Neo4j container'
        compadd -x 'stop        Stop Neo4j container'
        compadd -x 'start       Start Neo4j container'
        compadd -a neo4j_cmds
      fi
      ;;
    refresh|build|fast-build)
      if (( CURRENT == 3 )) || (( CURRENT == 4 && $words[3] == "run" )); then
        compadd -x 'Scope  Description'
        compadd -x 'f2     Fast 2 companies (development)'
        compadd -x 'm7     Magnificent 7 (default/PR)'
        compadd -x 'n100   NASDAQ 100 (validation)'
        compadd -x 'v3k    VTI 3500+ (production)'
        compadd -a scopes
      elif (( CURRENT == 3 && $cmd == "build" )); then
        compadd "run"
      fi
      ;;
    e2e)
      if (( CURRENT == 3 )); then
        compadd -x 'Scope  Description'
        compadd -x 'f2     Fast 2 companies (development)'
        compadd -x 'm7     Magnificent 7 (default/PR)'
        compadd -x 'n100   NASDAQ 100 (validation)'
        compadd -x 'v3k    VTI 3500+ (production)'
        compadd -a scopes
      fi
      ;;
    cleanup-branches)
      if (( CURRENT == 3 )); then
        compadd "--dry-run" "--auto"
      fi
      ;;
  esac
}

compdef -P _p3 **/my_finance/p3 p3


