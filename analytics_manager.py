from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import json

class AnalyticsManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_attendance_report(self, start_date=None, end_date=None):
        """Generate attendance report"""
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date
        
        # Get attendance data (this would need to be implemented in database_manager)
        attendance_data = self._get_attendance_range(start_date, end_date)
        
        report = {
            'period': f"{start_date} to {end_date}",
            'total_students': len(self.db.get_students()),
            'attendance_by_date': defaultdict(list),
            'student_statistics': defaultdict(int),
            'daily_totals': defaultdict(int)
        }
        
        for record in attendance_data:
            date = record.get('date', start_date)
            student_id = record.get('student_id')
            
            report['attendance_by_date'][date].append(record)
            report['student_statistics'][student_id] += 1
            report['daily_totals'][date] += 1
        
        return report
    
    def get_attendance_trends(self, days=30):
        """Get attendance trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trends = {
            'dates': [],
            'attendance_counts': [],
            'attendance_rates': []
        }
        
        total_students = len(self.db.get_students())
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            daily_attendance = self._get_daily_attendance_count(date_str)
            attendance_rate = (daily_attendance / total_students * 100) if total_students > 0 else 0
            
            trends['dates'].append(date_str)
            trends['attendance_counts'].append(daily_attendance)
            trends['attendance_rates'].append(round(attendance_rate, 2))
        
        return trends
    
    def get_student_performance(self, student_id=None):
        """Get individual student performance"""
        if student_id:
            return self._get_single_student_performance(student_id)
        
        students = self.db.get_students()
        performance_data = {}
        
        for student_data in students.values():
            sid = student_data['student_id']
            performance_data[sid] = self._get_single_student_performance(sid)
        
        return performance_data
    
    def _get_single_student_performance(self, student_id):
        """Get performance data for a single student"""
        # This would need database support
        last_30_days = self._get_student_attendance_last_30_days(student_id)
        
        return {
            'student_id': student_id,
            'total_days': 30,
            'attended_days': len(last_30_days),
            'attendance_rate': round((len(last_30_days) / 30) * 100, 2),
            'recent_attendance': last_30_days[-10:] if last_30_days else [],
            'streak': self._calculate_attendance_streak(last_30_days)
        }
    
    def _calculate_attendance_streak(self, attendance_dates):
        """Calculate current attendance streak"""
        if not attendance_dates:
            return 0
        
        # Sort dates and calculate consecutive days
        sorted_dates = sorted([datetime.strptime(date, "%Y-%m-%d") for date in attendance_dates])
        
        streak = 1
        for i in range(len(sorted_dates) - 1, 0, -1):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                streak += 1
            else:
                break
        
        return streak
    
    def export_to_excel(self, report_data, filename=None):
        """Export report to Excel"""
        if not filename:
            filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Summary sheet
                summary_df = pd.DataFrame([{
                    'Total Students': report_data['total_students'],
                    'Report Period': report_data['period'],
                    'Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Daily attendance sheet
                daily_data = []
                for date, records in report_data['attendance_by_date'].items():
                    for record in records:
                        daily_data.append({
                            'Date': date,
                            'Student ID': record.get('student_id'),
                            'Student Name': record.get('student_name'),
                            'Check-in Time': record.get('time')
                        })
                
                if daily_data:
                    daily_df = pd.DataFrame(daily_data)
                    daily_df.to_excel(writer, sheet_name='Daily Attendance', index=False)
            
            return True, f"Report exported to {filename}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def _get_attendance_range(self, start_date, end_date):
        """Get attendance data for date range - placeholder"""
        # This would need to be implemented in database_manager
        return []
    
    def _get_daily_attendance_count(self, date):
        """Get attendance count for specific date - placeholder"""
        # This would need to be implemented in database_manager
        return 0
    
    def _get_student_attendance_last_30_days(self, student_id):
        """Get student attendance for last 30 days - placeholder"""
        # This would need to be implemented in database_manager
        return []