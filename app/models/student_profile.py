from typing import Optional

from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    student_id: Optional[int] = Field(default=None, primary_key=True)

    # === STUDENT_SNIPPET_START ===
    # Complete the fields so a logged-in User can be matched to this Student
    # at runtime (your earlier choice: match by email, no User FK).
    #pass
    # === STUDENT_SNIPPET_END ===
    email: str = Field(unique=True, index=True)

class StudentProfile(SQLModel, table=True):
    profile_id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.student_id", unique=True, index=True)

    # === PROFILE_SNIPPET_START ===
    # Complete the fields shown on the Edit Student Profile wireframe
    # (including resume/CV storage as a field on this profile).
    #pass
    FullName : str = Field(index = True, unique = False)
    #Lname : str = Field(index = True, unique = False)
    UniversityMail: Optional[str] = Field(default=None, index = True, unique = True, nullable=True)
    Program: str = Field(index = True, unique = False)
    Year: int = Field(index = True, unique = False)
    InternshipPreference: Optional[str] = Field(default=None, index = True, unique = False, nullable=True)
    resume_cv: str = Field(nullable=True)
    # === PROFILE_SNIPPET_END ===


class InternshipPreference(SQLModel, table=True):
    preference_id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="studentprofile.profile_id", index=True)

    # === PREFERENCE_SNIPPET_START ===
    # Complete the fields for one selected preference option linked to a profile.
    industry: str = Field(nullable=True)
    location: str = Field(nullable=True)
    job_type: str = Field(nullable=True)
    job_level: str = Field(nullable=True)
    job_function: str = Field(nullable=True)
    job_title: str = Field(nullable=True)
    job_description: str = Field(nullable=True)
    job_requirements: str = Field(nullable=True)
    job_responsibilities: str = Field(nullable=True)
    # === PREFERENCE_SNIPPET_END ===
