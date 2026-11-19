from app import create_app, db
from app.models import CampusItem

app = create_app()

DATA = [
    ("academics", "Examination Cell", "Students can check examination schedules, hall tickets, internal assessments and results through the examination cell.", "Demo campus information"),
    ("academics", "Assignment Submission", "Students should submit assignments according to the deadline announced by their respective faculty or department.", "Demo campus information"),
    ("academics", "Attendance", "Students should regularly monitor their attendance and contact their department if they have questions about attendance records.", "Demo campus information"),
    ("academics", "Academic Timetable", "Class timetables are generally published by the concerned department. Students should check their department notice board or official portal for updates.", "Demo campus information"),
    
    ("faculty", "Faculty Information", "Faculty information should be checked through the concerned department office or official faculty directory.", "Demo campus information"),
    ("faculty", "Department Office", "Students can contact their department office for faculty-related academic queries, schedules and departmental information.", "Demo campus information"),

    ("campus", "Library", "The campus library provides students with a place to study and access academic resources. Students should check the library notice board for current timings.", "Demo campus information"),
    ("campus", "Computer Lab", "Computer laboratories are available for academic and practical work. Students should follow the laboratory rules and timings provided by their department.", "Demo campus information"),
    ("campus", "Campus Wi-Fi", "Students can contact the appropriate campus support or administration office for Wi-Fi access and connectivity issues.", "Demo campus information"),
    ("campus", "Canteen", "The campus canteen provides food and refreshments for students. Timings may vary according to campus schedules.", "Demo campus information"),

    ("events", "AI Workshop", "The campus may conduct technical workshops such as artificial intelligence, programming and emerging technology sessions. Students should check official announcements for registration and dates.", "Demo campus information"),
    ("events", "Hackathon", "Students interested in hackathons should regularly check official campus announcements and technical clubs for upcoming competitions.", "Demo campus information"),
    ("events", "Student Clubs", "Students can participate in technical, cultural and academic clubs according to the opportunities announced by the campus.", "Demo campus information"),

    ("notices", "Campus Notices", "Students should regularly check official notices and departmental announcements for important academic and administrative updates.", "Demo campus information"),
    ("notices", "Holiday Announcements", "Holiday schedules should be confirmed from official university or campus announcements because schedules can change.", "Demo campus information"),
    ("notices", "Important Deadlines", "Students should verify application, examination and registration deadlines from official announcements before submitting documents.", "Demo campus information"),

    ("services", "Student ID Card", "Students who need an ID card service should contact the appropriate student administration or office with the required documents.", "Demo campus information"),
    ("services", "Certificates", "Students can contact the concerned administration office for academic certificates and should confirm the required documents before applying.", "Demo campus information"),
    ("services", "Scholarships", "Students interested in scholarships should check official scholarship announcements and verify eligibility, documents and deadlines.", "Demo campus information"),
    ("services", "Student Help Desk", "Students can contact the appropriate campus help desk for assistance with administrative and student-service queries.", "Demo campus information"),
]

with app.app_context():
    db.create_all()

    CampusItem.query.delete()

    for category, title, content, source in DATA:
        db.session.add(
            CampusItem(
                category=category,
                title=title,
                content=content,
                source=source
            )
        )

    db.session.commit()

    print(f"Seeded {len(DATA)} campus knowledge items.")