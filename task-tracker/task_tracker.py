import MySQLdb


class TaskTracker:
    def __init__(self):
        self.db = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='12345678',
            db='task_tracker_db'
        )
        self.cursor = self.db.cursor()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS task
        (
          id             INT AUTO_INCREMENT
            PRIMARY KEY,
          task_name      VARCHAR(50) NOT NULL,
          status         VARCHAR(50) NOT NULL DEFAULT 'free',
          parent_task_id INT         NULL,
          worker_id      INT         NULL,
          CONSTRAINT parent_task_id_fk
          FOREIGN KEY (parent_task_id) REFERENCES task (id),
          CONSTRAINT task_worker_id_fk
          FOREIGN KEY (worker_id) REFERENCES user (id)
        )
          ENGINE = InnoDB;
        
        CREATE INDEX parent_task_id_fk
          ON task (parent_task_id);
        
        CREATE INDEX task_worker_id_fk
          ON task (worker_id);
        COMMIT; 
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user
        (
          id        INT AUTO_INCREMENT
            PRIMARY KEY,
          user_name VARCHAR(50) NOT NULL
        )
          ENGINE = InnoDB;
        COMMIT; 
        """)

    def create_user_and_tasks(self, users, tasks):
        name_users = ','.join([f"('{name}')" for name in users])
        self.cursor.execute("""
        INSERT INTO user
        (user_name)
        VALUES
         {};
        COMMIT; 
        """.format(name_users))
        for task in tasks:
            for task_parent, task_child_list in task.items():
                if task_child_list:
                    for task_child in task_child_list:
                        self.add_task(task_child, task_parent)
                else:
                    self.add_task(task_parent)

    def add_task(self, task_name, parent_name=None):
        if parent_name:
            parent_id = self._get_task_id(parent_name)
            if parent_id:
                self.cursor.execute("""
                INSERT INTO task
                (task_name, parent_task_id)
                VALUES ('{}', '{}');
                COMMIT;
                """.format(task_name, parent_id[0]))
            else:
                self.add_task(parent_name)
                self.add_task(task_name, parent_name)
        else:
            self.cursor.execute("""
            INSERT INTO task
            (task_name)
            VALUES ('{}');
            COMMIT;
            """.format(task_name))

    def get_task(self, user_name, task_name):
        user_id = self._get_user_id(user_name)
        assert user_id, 'Такого пользователя нету'
        task_id = self._get_task_id(task_name)
        assert task_id, 'Такой задачи нету'
        self.cursor.execute("""
        SELECT task_name FROM task
        WHERE parent_task_id='{}';
        """.format(task_id[0]))
        for task_child in self.cursor.fetchall():
            self.get_task(user_name, task_child[0])
        self.cursor.execute("""
        UPDATE task SET status='in work', worker_id='{}'
        WHERE task_name='{}' AND status='free';
        COMMIT;
        """.format(user_id[0], task_name))

    def set_finish(self, task_name):
        task_id = self._get_task_id(task_name)
        assert task_id, 'Такой задачи нету'
        self.cursor.execute("""
        SELECT task_name FROM task
        WHERE parent_task_id='{}';
        """.format(task_id[0]))
        for task_child in self.cursor.fetchall():
            self.set_finish(task_child[0])
        self.cursor.execute("""
        UPDATE task SET status='finish', worker_id=NULL 
        WHERE task_name='{}' AND status='in work';
        COMMIT;
        """.format(task_name))

    def check_status(self, name):
        self.cursor.execute("""
        SELECT status FROM task
        WHERE task_name='{}'
        LIMIT 1;
        """.format(name))
        return self.cursor.fetchone()

    def _get_user_id(self, name):
        self.cursor.execute("""
        SELECT id FROM user
        WHERE user_name='{}';
        """.format(name))
        return self.cursor.fetchone()

    def _get_task_id(self, name):
        self.cursor.execute("""
        SELECT id FROM task
        WHERE task_name='{}';
        """.format(name))
        return self.cursor.fetchone()

    def see_all_tasks(self):
        self.cursor.execute("""
        select * from `task`
        """)
        print(*self.cursor.fetchall(), sep='\n')


if __name__ == '__main__':
    start_data = {
        'users': ['Anton', 'Vadim', 'Misha'],
        'tasks': [
            {'task_1': []},
            {'task_2': ['task_3']},
            {'task_3': ['task_4', 'task_5']},
        ]
    }
    m = TaskTracker()
    m.get_task('Anton', 'task_2')
    m.create_user_and_tasks(**start_data)
    m.set_finish('hello')
    m.add_task('One', 'Who')
    m.see_all_tasks()
    print(m.check_status('task_3'))
