CREATE TABLE users (
  user_id BIGSERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL
);

CREATE TABLE tools (
  tool_id BIGSERIAL PRIMARY KEY,
  short_name TEXT NOT NULL,
  long_name TEXT NOT NULL
);

CREATE TABLE user_access (
  user_id BIGINT REFERENCES users ON DELETE CASCADE,
  tool_id BIGINT REFERENCES tools,
  PRIMARY KEY (user_id, tool_id),
  CONSTRAINT user_tool_unique UNIQUE (user_id, tool_id));
