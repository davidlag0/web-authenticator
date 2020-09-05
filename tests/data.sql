INSERT INTO users (username,email)
VALUES
  ('testuser_allaccess','email1@email.com'),
  ('testuser_noaccess','email2@email.com');

INSERT INTO tools (short_name,long_name)
VALUES
  ('kibana','Kibana'),
  ('jenkins','Jenkins');

INSERT INTO user_access (user_id,tool_id)
VALUES
  ((SELECT user_id FROM users WHERE username='testuser_allaccess'),(SELECT tool_id FROM tools WHERE short_name='kibana'))
  ((SELECT user_id FROM users WHERE username='testuser_allaccess'),(SELECT tool_id FROM tools WHERE short_name='jenkins'));
