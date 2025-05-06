import argparse
from pathlib import Path

from shell_stack.shell_stack_app import ShellStackApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Shell Stack")
    parser.add_argument("-c", "--config", type=str, help="Path to SSH config file")
    parser.add_argument("-t", "--refresh-interval", type=int, help="Refresh interval in seconds")
    args = parser.parse_args()

    ssh_config_path = Path(args.config) if args.config else None
    if ssh_config_path and not ssh_config_path.exists():
        raise FileNotFoundError(f"SSH config file '{ssh_config_path}' does not exist")  # noqa: TRY003

    refresh_interval = args.refresh_interval if args.refresh_interval else None

    app = ShellStackApp(
        ssh_config_path=ssh_config_path,
        refresh_interval=refresh_interval,
    )
    # Suspending does not work with inline=True
    app.run(inline=False)


if __name__ == "__main__":
    # Run using `run shell_stack/main.py`. Add `--dev` to run in dev mode.
    # For dev mode, run `textual console` in a separate terminal to get the dev logs
    main()

# TODO: What's the legit way of running the ssh command?
# TODO: Add tests
# TODO: Update README and CONTRIBUTING
#          - mention that we do not support <3.10 because of typehints
# TODO: Push v1
# TODO: Add pypi build
