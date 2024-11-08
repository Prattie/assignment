import pandas as pd

def check_eligibility(student_info):
    """
    Check program eligibility based on student information
    Returns a list of eligible programs
    """
    try:
        # Define the program data directly (from your Google Sheet)
        programs_data = {
            'programs': [
                {
                    'university': 'Case Western Reserve University',
                    'program': 'Master of Business Analytics and Intelligence',
                    'percentage': 75,
                    'backlogs': 0,
                    'work_experience': 2,
                    'three_year_degree': 'Not Allowed'
                },
                {
                    'university': 'Rutgers University',
                    'program': 'Master of Information Technology and Analytics',
                    'percentage': 62,
                    'backlogs': 2,
                    'work_experience': 2,
                    'three_year_degree': 'Allowed'
                },
                {
                    'university': 'Fairfield University',
                    'program': 'MS in Business Analytics',
                    'percentage': 70,
                    'backlogs': 0,
                    'work_experience': 1,
                    'three_year_degree': 'Allowed'
                },
                # Add more programs as needed
            ]
        }

        # Initialize list for eligible programs
        eligible_programs = []

        # Extract basic information (handle missing data gracefully)
        student_name = student_info.get('name', '')
        timeline = student_info.get('timeline', '')

        # Log the received student info for debugging
        print(f"Received student info: {student_info}")

        # For now, return all programs (we'll add filtering logic later)
        for program in programs_data['programs']:
            eligible_programs.append({
                'university': program['university'],
                'program': program['program'],
                'requirements': {
                    'percentage': program['percentage'],
                    'backlogs': program['backlogs'],
                    'work_experience': program['work_experience'],
                    'three_year_degree': program['three_year_degree']
                }
            })

        return eligible_programs

    except Exception as e:
        print(f"Error in eligibility check: {str(e)}")
        # Return a default response if there's an error
        return [{
            'university': 'University Advisor',
            'program': 'Please consult with our advisors',
            'requirements': {
                'percentage': 'Contact advisor',
                'backlogs': 'Contact advisor',
                'work_experience': 'Contact advisor',
                'three_year_degree': 'Contact advisor'
            }
        }]

def format_eligibility_response(eligible_programs):
    """Format the eligibility results into a readable response"""
    if not eligible_programs:
        return "Based on your profile, I couldn't find any exact matches. However, I recommend scheduling a consultation to discuss alternative options."
    
    response = "Based on your profile and preferences, here are the programs you're eligible for:\n\n"
    
    for program in eligible_programs:
        response += f"🎓 {program['program']} at {program['university']}\n"
        response += "Program Details:\n"
        response += f"- Duration: 2 years\n"
        response += f"- Location: {program['university']} Campus\n"
        response += f"- Minimum Percentage Required: {program['requirements']['minimum_percentage']}%\n"
        response += f"- Maximum Backlogs Allowed: {program['requirements']['maximum_backlogs']}\n"
        response += f"- Work Experience Required: {program['requirements']['work_experience']} years\n"
        response += f"- Three Year Degree: {program['requirements']['three_year_degree']}\n\n"
        response += "Would you like to learn more about this program?\n\n"

    response += "I can provide more details about any of these programs or help you schedule a consultation with our advisors."
    
    return response

if __name__ == "__main__":
    # Test the functions
    test_student = {
        "name": "Test Student",
        "timeline": "Fall 2024"
    }
    
    eligible = check_eligibility(test_student)
    response = format_eligibility_response(eligible)
    print(response)
