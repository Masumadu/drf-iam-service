class TodoTestData:
    def existing_todo(self, user_id):
        return {"todo": "test_todo", "user_id": user_id}

    @property
    def create_todo(self):
        return {"todo": "new_todo"}

    def update_todo(self, completed=False):
        return {"completed": completed}
