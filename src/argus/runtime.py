import argparse
import logging
import queue
import threading
from typing import Optional

from argus.config import AgentConfig
from argus.doctor import run_doctor


def run_smart_agent(task_description: str, force_agent: Optional[str] = None):
    from argus.agents.smart_router import get_router

    print(f"\n{'=' * 60}")
    print("🤖 智能任务路由器")
    print(f"任务: {task_description}")
    print(f"模式: {'强制 ' + force_agent.upper() + 'Agent' if force_agent else '自动判断 + 失败切换'}")
    print(f"{'=' * 60}\n")

    router = get_router()
    message_from_client = queue.Queue()
    message_to_client = queue.Queue()

    stop_flag = threading.Event()

    def listen_to_agent():
        while not stop_flag.is_set():
            try:
                msg = message_to_client.get(timeout=0.5)
                msg_type = msg.get("type", "")
                content = msg.get("content", "")

                if msg_type == "status":
                    if content == "[START]":
                        print("[状态] Agent已启动")
                    elif content == "[STOP]":
                        print("\n[状态] Agent已停止")
                        stop_flag.set()
                        break
                elif msg_type == "ai_content":
                    if content not in ["[BEGIN]", "[END]"]:
                        print(content, end="", flush=True)
                elif msg_type == "text":
                    print(f"\n{content}")
                elif msg_type == "tool_result":
                    tool_info = content
                    print(f"\n[工具] {tool_info.get('function')}: {'成功' if tool_info.get('success') else '失败'}")
                elif msg_type == "request" and "need_permission" in content:
                    print("\n[请求] 自动批准代码执行")
                    message_from_client.put({"type": "request", "content": "approve"})
            except queue.Empty:
                continue
            except Exception as exc:
                logging.error("消息监听错误: %s", exc)

    listener = threading.Thread(target=listen_to_agent, daemon=True)
    listener.start()

    try:
        result = router.execute_with_fallback(
            task_description,
            message_from_client,
            message_to_client,
            force_agent=force_agent,
        )
        print(f"\n\n✓ 任务结果: {result}")
    except KeyboardInterrupt:
        print("\n用户中断")
        stop_flag.set()
    except Exception as exc:
        logging.error("执行错误: %s", exc, exc_info=True)
        print(f"\n✗ 错误: {exc}")

    stop_flag.set()
    listener.join(timeout=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Argus - 智能任务路由器")
    parser.add_argument("--task", type=str, required=False, help="任务描述")
    parser.add_argument("--force", type=str, choices=["gui", "code"], help="强制使用特定Agent")
    parser.add_argument("--doctor", action="store_true", help="运行环境自检")
    return parser


def print_doctor_result(result: dict) -> None:
    print("\nArgus Doctor")
    print("=" * 60)
    for item in result["checks"]:
        print(f"[{item['status'].upper():4s}] {item['name']:14s} {item['detail']}")
    print("-" * 60)
    print(f"Summary: pass={result['passed']} warn={result['warned']} fail={result['failed']}")


def run_cli(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    config = AgentConfig.from_env()
    if args.doctor:
        result = run_doctor(config)
        print_doctor_result(result)
        raise SystemExit(1 if result["failed"] > 0 else 0)

    if not args.task:
        parser.error("--task is required unless --doctor is used")

    from argus.bootstrap import setup_environment

    setup_environment()

    missing_env = config.missing_required()
    if missing_env:
        print(f"❌ 错误: 命令行模式检测到配置缺失: {', '.join(missing_env)}")
        raise SystemExit(1)

    run_smart_agent(args.task, args.force)


def run_gui():
    from argus.bootstrap import setup_environment

    setup_environment()
    print("启动 Argus Liquid Bar UI...")
    try:
        from argus.ui.app import start_gui_app

        start_gui_app()
    except ImportError as exc:
        print(f"UI依赖缺失: {exc}")
        print("请运行: uv sync")
    except Exception as exc:
        print(f"UI启动失败: {exc}")
        import traceback

        traceback.print_exc()


def main(argv: list[str] | None = None):
    if argv is None:
        import sys

        argv = sys.argv[1:]

    if argv:
        run_cli(argv)
    else:
        run_gui()
