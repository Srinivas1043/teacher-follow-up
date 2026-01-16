-- Enable UUID extension (usually enabled by default, but good to ensure)
create extension if not exists "uuid-ossp";

-- Create STUDENTS table
create table students (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null, -- Links to the logged-in teacher
  name text not null,
  grade text,
  notes text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create FOLLOWUPS table
create table followups (
  id uuid default uuid_generate_v4() primary key,
  student_id uuid references students(id) on delete cascade not null,
  content text not null, -- The generated message
  original_remarks text, -- What the teacher typed
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
-- This is CRITICAL so teachers only see THEIR OWN students
alter table students enable row level security;
alter table followups enable row level security;

-- Policy: Teachers can only see students they created
create policy "Individuals can view their own students"
on students for select
using ( auth.uid() = user_id );

create policy "Individuals can insert their own students"
on students for insert
with check ( auth.uid() = user_id );

-- Policy: Teachers can only see followups for students they own
-- (A bit more complex join, but for simplicity we rely on the student link)
create policy "Individuals can view their own student followups"
on followups for select
using ( 
  exists (
    select 1 from students 
    where students.id = followups.student_id 
    and students.user_id = auth.uid()
  )
);

create policy "Individuals can insert their own student followups"
on followups for insert
with check (
  exists (
    select 1 from students 
    where students.id = followups.student_id 
    and students.user_id = auth.uid()
  )
);
