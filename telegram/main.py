from bots.admin.bot import start

def main():
    start()

if __name__ == "__main__":
    main()

# from threading import Thread

# from bots.admin.bot import start as start_admin
# from bots.public.bot import start as start_public


# def main():
#     Thread(target=start_admin, daemon=True).start()
#     Thread(target=start_public, daemon=True).start()

#     Thread(target=lambda: None).join()


# if __name__ == "__main__":
#     main()