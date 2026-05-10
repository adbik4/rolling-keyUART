import os
import fcntl
import select
import errno

from TokenGenerator import TokenGenerator

TRIES = 1000
SECRET_KEY = "enter_password_here"
UART_DEVICE = "/dev/ttyS0"

def verify_msg(gen, msg):
    """
    Checks if the recieved key hash was valid.
    The server will check a specified number of counter values before giving up
    """
    count = 0
    while count < TRIES:
        if msg == gen.generate_token(SECRET_KEY):
            return True
        count += 1
        
    return False

def enable_LED_G():
    # lights the green LED
    pass
    
def enable_LED_R():
    # lights the red LED
    pass
    
def disable_LEDs():
    # turns off all LEDs
    pass

def main():
    # Create hash token generator insance
    gen = TokenGenerator(SECRET_KEY)
    
    # Open a Serial file descrpitor and configure it as nonblocking 
    fd = os.open(UART_DEVICE, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    
    # Create epoll instance
    epoll = select.epoll()
    epoll.register(fd, select.EPOLLIN)

    buffer = ""

    print("Waiting for UART data...")

    try:
        while True:
            disable_LEDs()
            events = epoll.poll(-1)  # block until event

            for fileno, event in events:
                if fileno == fd and event & select.EPOLLIN:
                    try:
                        data = os.read(fd, 1024).decode(errors="ignore")
                    except OSError as e:
                        if e.errno != errno.EAGAIN:
                            raise
                        continue

                    if not data:
                        continue

                    buffer += data

                    # Process full lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if verify_msg(gen, line):
                            enable_LED_G()
                        else:
                            enable_LED_R()

                elif event & (select.EPOLLHUP | select.EPOLLERR):
                    print("UART closed or error")
                    return

    finally:
        epoll.unregister(fd)
        epoll.close()
        os.close(fd)


if __name__ == "__main__":
    main()