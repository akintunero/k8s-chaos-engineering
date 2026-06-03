#!/usr/bin/env python3
"""
Unified CLI for k8s-chaos-engineering.

Install: pip install -e .
Usage:   k8s-chaos doctor | preflight | list | run | abort | report | gameday | clusters
"""

from __future__ import annotations

import argparse
import os
import sys


def _repo_root():
    from k8s_chaos.utils.catalog import repo_root

    return repo_root()


def cmd_doctor(args: argparse.Namespace) -> int:
    from k8s_chaos.doctor import (
        check_cluster,
        check_litmus,
        check_quickstart_app,
        check_tool,
    )

    ok = True
    ok = check_tool("kubectl", "kubectl version --client") and ok
    ok = check_tool("helm", "helm version --short") and ok
    ok = check_tool("python3", "python3 --version") and ok
    ok = check_cluster() and ok
    if args.full:
        from k8s_chaos.utils import get_config

        cfg = get_config()
        ok = check_litmus(cfg.litmus_namespace) and ok
        ok = check_quickstart_app(cfg.app_namespace) and ok
    return 0 if ok else 1


def cmd_preflight(args: argparse.Namespace) -> int:
    from k8s_chaos.preflight import run_preflight
    from k8s_chaos.utils import get_logger

    logger = get_logger("cli")
    if not run_preflight(
        args.namespace,
        require_litmus=not args.skip_litmus,
        require_app=not args.skip_app,
    ):
        return 1
    logger.info("Pre-flight passed")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    from k8s_chaos import chaos_runner
    from k8s_chaos.utils.logging import get_logger

    logger = get_logger("cli")

    if args.gamedays:
        from k8s_chaos.utils.catalog import list_gameday_workflows

        for name in list_gameday_workflows():
            logger.info("  gameday: %s", name)
        return 0

    if args.clusters:
        from k8s_chaos.utils.clusters import list_clusters

        for c in list_clusters():
            logger.info("  cluster: %s (context=%s, env=%s)", c.name, c.context, c.chaos_env)
        return 0

    experiments = chaos_runner.list_experiments()
    logger.info("Experiments (CHAOS_ENV=%s):", os.getenv("CHAOS_ENV", "dev"))
    for exp in experiments:
        logger.info("  - %s", exp)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if args.cluster:
        from k8s_chaos.multicluster import run_experiment_on_clusters

        results = run_experiment_on_clusters(args.experiment, [args.cluster])
        return 0 if all(r.get("verdict") == "PASS" for r in results) else 1

    from k8s_chaos import chaos_runner

    chaos_runner.run_experiment(args.experiment)
    return 0


def cmd_abort(args: argparse.Namespace) -> int:
    if args.all_namespaces:
        from k8s_chaos.abort import main as abort_main

        sys.argv = ["abort", "--all-namespaces"]
        abort_main()
        return 0
    from k8s_chaos.abort import abort_namespace
    from k8s_chaos.utils import get_config

    namespace = args.namespace or get_config().app_namespace
    abort_namespace(namespace)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from k8s_chaos.quickstart_report import main as report_main

    sys.argv = [
        "quickstart_report",
        "--experiment",
        args.experiment,
        "--output-dir",
        args.output_dir,
    ]
    if args.namespace:
        sys.argv.extend(["--namespace", args.namespace])
    report_main()
    return 0


def cmd_gameday(args: argparse.Namespace) -> int:
    if args.cluster:
        from k8s_chaos.multicluster import run_gameday_on_clusters

        results = run_gameday_on_clusters(args.workflow, [args.cluster])
        return 0 if all(r.get("verdict") == "PASS" for r in results) else 1

    from k8s_chaos.gameday import execute_gameday, load_workflow
    from k8s_chaos.gameday import main as gameday_main

    if args.list:
        sys.argv = ["gameday", "--list"]
        gameday_main()
        return 0

    from k8s_chaos.utils.catalog import repo_root
    from k8s_chaos.utils.reporting import print_gameday_summary, write_report

    report = execute_gameday(args.workflow, skip_preflight=args.skip_preflight)
    path = write_report(
        report,
        repo_root() / args.output_dir,
        basename=f"gameday-{args.workflow}",
    )
    print_gameday_summary(report, path)
    if report.get("verdict") != "PASS":
        return 1
    return 0


def cmd_clusters(args: argparse.Namespace) -> int:
    from k8s_chaos.multicluster import (
        run_experiment_on_clusters,
        run_gameday_on_clusters,
    )
    from k8s_chaos.utils.clusters import list_clusters, resolve_clusters
    from k8s_chaos.utils.logging import get_logger

    logger = get_logger("cli")
    names = resolve_clusters(args.names, allow_prod=args.allow_prod)
    if not names:
        logger.error("No clusters matched")
        return 1

    if args.gameday:
        results = run_gameday_on_clusters(args.gameday, names, allow_prod=args.allow_prod)
    elif args.experiment:
        results = run_experiment_on_clusters(args.experiment, names, allow_prod=args.allow_prod)
    else:
        for c in list_clusters():
            if not names or c.name in names:
                logger.info("%s  context=%s  env=%s", c.name, c.context, c.chaos_env)
        return 0

    failed = [r for r in results if r.get("verdict") != "PASS"]
    for r in results:
        logger.info("[%s] %s", r.get("verdict"), r.get("cluster"))
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="k8s-chaos",
        description="Kubernetes chaos engineering CLI (Litmus quickstart kit)",
    )
    sub = parser.add_subparsers(dest="command", required=False)

    p = sub.add_parser("doctor", help="Check kubectl, helm, cluster")
    p.add_argument("--full", action="store_true")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("preflight", help="Pre-flight before chaos")
    p.add_argument("--namespace", default=None)
    p.add_argument(
        "--skip-app",
        action="store_true",
        help="Skip quickstart application health check (e.g. after kubectl wait in quickstart)",
    )
    p.add_argument(
        "--skip-litmus",
        action="store_true",
        help="Skip Litmus CRD and namespace checks",
    )
    p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("list", help="List experiments, gamedays, or clusters")
    p.add_argument("--gamedays", action="store_true")
    p.add_argument("--clusters", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("run", help="Run a chaos experiment")
    p.add_argument("experiment")
    p.add_argument("--cluster", default=None, help="Run on registered cluster")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("abort", help="Abort all chaos engines")
    p.add_argument("--namespace", default=None)
    p.add_argument("--all-namespaces", action="store_true")
    p.set_defaults(func=cmd_abort)

    p = sub.add_parser("report", help="SLO report for an experiment")
    p.add_argument("experiment", nargs="?", default="pod-delete")
    p.add_argument("--namespace", default=None)
    p.add_argument("--output-dir", default="reports")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("gameday", help="Run a GameDay workflow")
    p.add_argument("workflow", nargs="?", default="quickstart")
    p.add_argument("--list", action="store_true")
    p.add_argument("--cluster", default=None)
    p.add_argument("--skip-preflight", action="store_true")
    p.add_argument("--output-dir", default="reports")
    p.set_defaults(func=cmd_gameday)

    p = sub.add_parser("clusters", help="Multi-cluster operations")
    p.add_argument("names", nargs="*", help="Cluster names (empty = list)")
    p.add_argument("--experiment", default=None)
    p.add_argument("--gameday", default=None)
    p.add_argument("--allow-prod", action="store_true")
    p.set_defaults(func=cmd_clusters)

    return parser


def main() -> None:
    from k8s_chaos import __version__
    from k8s_chaos.runtime import command_needs_runtime_tools, require_runtime_tools

    parser = build_parser()
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(2)
    if command_needs_runtime_tools(args.command, args):
        require_runtime_tools()
    try:
        code = args.func(args)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    except Exception as exc:
        from k8s_chaos.utils.logging import get_logger

        get_logger("cli").error("Command failed: %s", exc, exc_info=True)
        code = 1
    sys.exit(code or 0)


if __name__ == "__main__":
    main()
