import hashlib
import os
import secrets
import string
import argparse
import serial
from TokenGenerator import TokenGenerator

class TokenClient:
    def __init__(self, shared_key: str, dev: str, counter_file: str = "counter.txt"):
        self.shared_key = shared_key
        self.counter_file = counter_file
        self.dev = dev

        try:
            self.uart = serial.Serial(port=self.dev, baudrate=9600, timeout=1)
            print(f"Successfully opened UART port: {self.dev}")
        except serial.SerialException as e:
            print(f"[WARNING] Failed to open UART port {self.dev}: {e}")
            self.uart = None

        initial_counter = self._load_counter()
        self.generator = TokenGenerator(self.shared_key, initial_counter)

    def _load_counter(self) -> int:
        """Load counter value from file, or return 0 if file does not exist."""
        if os.path.exists(self.counter_file):
            try:
                with open(self.counter_file, 'r') as file:
                    return int(file.read().strip())
            except ValueError:
                return 0
        return 0

    def _save_counter(self):
        """Save actual value of counter into the file"""
        with open(self.counter_file, 'w') as file:
            file.write(str(self.generator.counter))

    def _send_code(self, code: str):
        """Send code over UART, or print if UART is not present."""
        if self.uart and self.uart.is_open:
            try:
                message = f"{code}\n".encode('utf-8')
                self.uart.write(message)
                print(f"--> Sent via UART [{self.dev}]: {code}")
            except serial.SerialException as e:
                print(f"[ERROR] Problem during UART transmission: {e}")
        else:
            print(f"Generated code (UART unavailable, preview only): {code}")

    def execute_command(self, command: str, forward_step: int = 0):
        """Method for executing shell commands."""

        if command == "gen":
            code = self.generator.generate_token()
            self._send_code(code)
            self._save_counter()

        elif command == "gen_rand":
            random_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

            temp_generator = TokenGenerator(random_key, self.generator.counter)
            code = temp_generator.generate_token()

            self._send_code(code)

        elif command == "gen_forward":
            new_counter = self.generator.counter + forward_step
            self.generator = TokenGenerator(self.shared_key, new_counter)
            code = self.generator.generate_token()
            self._send_code(code)
            self._save_counter()

        else:
            print(f"Unknown command: {command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Client CLI with UART support")
    parser.add_argument("--dev", type=str, required=True, help="Path to UART device (e.g. /dev/ttyUSB0)")
    parser.add_argument("--key", type=str, default="enter_password_here", help="Shared key for hash")
    args = parser.parse_args()

    klient = TokenClient(shared_key=args.key, dev=args.dev)

    print("\n=============================================")
    print("  TokenClient Shell started!")
    print("  Available commands: gen, gen_rand, gen_forward <x>, exit")
    print("=============================================\n")

    while True:
        try:
            user_input = input("TokenShell> ").strip().split()

            if not user_input:
                continue

            cmd = user_input[0].lower()

            if cmd in ["exit", "quit"]:
                print("Closing shell...")
                if klient.uart and klient.uart.is_open:
                    klient.uart.close()
                break

            elif cmd == "gen":
                klient.execute_command("gen")

            elif cmd == "gen_rand":
                klient.execute_command("gen_rand")

            elif cmd == "gen_forward":
                if len(user_input) > 1:
                    try:
                        step = int(user_input[1])
                        klient.execute_command("gen_forward", forward_step=step)
                    except ValueError:
                        print("Error: Argument for gen_forward must be an integer.")
                else:
                    print("Error: Step not provided! Proper usage: gen_forward 5")
            else:
                print(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\nInterrupted by user (Ctrl+C). Closing...")
            if klient.uart and klient.uart.is_open:
                klient.uart.close()
            break
