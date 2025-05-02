

from grpc_clients.user import register_user

if __name__ == "__main__":
    user_id = register_user(
        username="johndoe",
        email="john@example.com",
        password="secure123"
    )
    print(f"Registered user ID: {user_id}")