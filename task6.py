from enum import Enum
from collections.abc import Set
from collections.abc import Sequence


class MessageType(Enum):
    TEXT = 1
    IMAGE = 2
    STICKER = 3
    VIDEO = 4


class User:
    def __init__(self, nickname: str, phone: str, email: str, first_name: str, last_name: str,
                 direct_messages: dict, chats: set, friends: set):
        self.nickname = nickname
        self.phone = phone
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.direct_messages = direct_messages
        self.chats = chats
        self.friends = friends

    def __str__(self):
        return self.first_name + " " + self.last_name


class Message:
    def __init__(self, m_type: MessageType, sender: str, receiver: str, payload: str | bytearray):
        self.m_type = m_type
        self.sender = sender
        self.receiver = receiver
        self.payload = payload

    def __str__(self):
        return f"{self.__get_peer(self.sender)} -> {self.__get_peer(self.receiver)}: {self.payload}"

    def __get_peer(self, p: str):
        if self.messanger is not None:
            if p in self.messanger.chats.keys():
                return "all"
            elif p in self.messanger.users.keys():
                return str(self.messanger.users[p])
        return p

class Chat:
    def __init__(self, gid: str, name: str, members: Set[str], messages: Sequence[Message]):
        self.gid = gid
        self.name = name
        self.members = members
        self.messages = messages

    def add_user(self, u: User):
        self.members.add(u.nickname)
        u.chats.add(self.gid)

    def add_message(self, msg: Message):
        self.messages.append(msg)
        msg.messanger = self.messanger

    def add_text_message(self, u: User, msg: str):
        self.add_message(
            Message(MessageType.TEXT, u.nickname, self.gid, msg)
        )

    def find_messages_with_words(self, words: Sequence[str]):
        return tuple(filter(
            lambda msg: msg.m_type == MessageType.TEXT and all([msg.payload.lower().find(w.lower()) >= 0 for w in words]),
            self.messages
        ))

    def __str__(self):
        return f"{self.name}: {len(self.members)} user(s)"


class Messenger:
    def __init__(self, users: dict, chats: dict):
        self.users = users
        self.chats = chats
        for u in users.values():
            u.messanger = self
        for c in chats.values():
            c.messanger = self

    def get_shared_chats(self, users: Sequence[User]):
        return list(map(
            lambda gid: self.chats.get(gid),
            set.intersection(*list(map(
                lambda u: u.chats,
                users
            )))
        ))


if __name__ == '__main__':
    # init with some data
    student_chat = Chat(
        "gid1", "student chat",
        {"john1999", "james66", "anna2001"},
        [
            Message(MessageType.TEXT, "anna2001", "gid1", "Hello everybody!"),
            Message(MessageType.TEXT, "james66", "gid1", "Hi Anna!"),
            Message(MessageType.TEXT, "john1999", "anna2001", "Hello!")
        ]
    )
    python_learners = Chat(
        "gid2", "we learn python",
        {"james66", "anna2001"},
        []  # no messages yet
    )
    book_readers = Chat(
        "gid3", "we read books",
        set(),  # no users yet
        []   # no messages yet
    )

    john = User("john1999", "123456789", "john@gmail.com", "John", "Johnson", {}, {"gid1"}, set())
    james = User("james66", "987654321", "james@mipt.ru", "James", "Jameson", {}, {"gid1", "gid2"}, {"anna2001"})
    anna = User(
        "anna2001", "1122334455", "anna@yandex.ru", "Anna", "Peterson",
        {
            "james66": [Message(MessageType.TEXT, "anna2001", "james66", "Hi James, do you know python?")]
        },
        {"gid1", "gid2"}, {"james66"}
    )

    messanger = Messenger(
        {
            "john1999": john,
            "james66": james,
            "anna2001": anna
        },
        {
            "gid1": student_chat,
            "gid2": python_learners,
            "gid3": book_readers
        }
    )

    # test methods
    book_readers.add_user(james)
    book_readers.add_user(anna)

    python_learners.add_user(john)
    python_learners.add_text_message(john, "Hello everyone!")
    python_learners.add_text_message(john, "How are you?")
    python_learners.add_text_message(anna, "Ready to learn python!")
    python_learners.add_text_message(james, "Me too!")
    python_learners.add_text_message(james, "Hey python, ready or not, I'm here!")

    print(f"Full '{python_learners.name}' chat:")
    print('\n'.join(list(map(str, python_learners.messages))))

    keywords = ["python", "ready"]
    print(f"Search in '{python_learners.name}' by words: [{keywords}]")
    print('\n'.join(list(map(str, python_learners.find_messages_with_words(keywords)))))

    some_users = [anna, james]
    print(f"Common chats for {list(map(str, some_users))}:")
    # all 3 groups expected
    print(list(map(str, messanger.get_shared_chats(some_users))))

    other_users = [anna, john]
    print(f"Common chats for {list(map(str, other_users))}:")
    # book reading group is not expected
    print(list(map(str, messanger.get_shared_chats(other_users))))

