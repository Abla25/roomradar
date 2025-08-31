const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Initialize Firebase Admin
admin.initializeApp();

// Function to log when a report is created (for monitoring)
exports.logReportCreated = functions.firestore
  .document('reports/{reportId}')
  .onCreate(async (snap, context) => {
    const reportData = snap.data();
    
    try {
      console.log('🚨 New report created:', {
        reportId: context.params.reportId,
        userId: reportData.userId,
        userEmail: reportData.userEmail,
        reportType: reportData.reportType,
        listingTitle: reportData.listingTitle,
        createdAt: reportData.createdAt
      });
      
      return { success: true, reportId: context.params.reportId };
    } catch (error) {
      console.error('❌ Error logging report:', error);
      return { success: false, error: error.message };
    }
  });
