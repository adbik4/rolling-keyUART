import os
import fcntl
import select
import errno

from TokenGenerator import TokenGenerator

class TokenServer:
    def __init__(self, shared_key: str, retries: int, dev: str = "/dev/ttys0", counter_file: str = "counter.txt"):
        self.buffer = ""
        self.dev = dev
        self.shared_key = shared_key
        self.counter_file = counter_file
        self.retries = retries
        self.initial_counter = 0
        self.uart = None
        self.poll = None

        try:
            # Open a Serial file descrpitor and configure it as nonblocking
            open_flags = os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK
            self.uart = os.open(dev, open_flags)
            flags = fcntl.fcntl(self.uart, fcntl.F_GETFL)
            fcntl.fcntl(self.uart, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        except OSError:
            print(f"Error: Device {self.dev} not found")
            quit()

        try:
            self.poll = select.poll()
            self.poll.register(self.uart, select.POLLIN)
        except OSError:
            print(f"Error: device {self.dev} cannot be monitored by poll")
            quit()

        self.initial_counter = self._load_counter()
        self.generator = TokenGenerator(self.shared_key, self.initial_counter)

    def __del__(self):
        if self.uart is not None:
            try:
                os.close(self.uart)
            except Exception:
                pass
            if self.poll is not None:
                try:
                    self.poll.unregister(self.uart)
                except Exception:
                    pass
                try:
                    self.poll.close()
                except Exception:
                    pass

        if self.initial_counter > 0:
            self._save_counter()

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

    def _verify_msg(self, msg: str) -> bool:
        """
        Verifies if the recieved key hash was valid.
        The server will check a specified number of counter values before giving up
        """
        count = 0
        while count < self.retries:
            expected = self.generator.generate_token()
            if msg.strip() == expected:
                return True
            count += 1

        return False

    def handle_event(self) -> int:
        """
        Handles a poll event
        """
        if self.uart is None:
            return -1

        try:
            raw = os.read(self.uart, 1024)
            data = raw.decode(errors="ignore")
        except OSError as e:
            if e.errno != errno.EAGAIN:
                raise
            return -1

        if not data:
            return -1

        self.buffer += data

        # Process full lines
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if self._verify_msg(line):
                return 1
            else:
                return 0

        return -1

def enable_LED_G():
    # lights the green LED
    pass

def enable_LED_R():
    # lights the red LED
    pass

def disable_LEDs():
    # turns off all LEDs
    pass


if __name__ == "__main__":
    server = TokenServer("enter_password_here", 1000)

    print("Waiting for UART data...")

    while True:
        disable_LEDs()
        poller = server.poll
        if poller is None:
            print("Error: poll was not initialized")
            quit()

        events = poller.poll(-1)  # block until event
        for fd, event in events:
            if fd == server.uart and event & select.POLLIN:
                status = server.handle_event()
                if status < 0:
                    continue
                elif status == 1:
                    enable_LED_G()
                elif status == 0:
                    enable_LED_R()
            elif event & (select.POLLHUP | select.POLLERR):
                print("Error: UART closed or failed")
                quit()