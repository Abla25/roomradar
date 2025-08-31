// Reports Management for RoomRadar
// Handles reporting listings with Firebase, Email, and Notion integration

import { getFirestore, doc, setDoc, collection, addDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// Report types available
export const REPORT_TYPES = {
  SPAM: 'spam',
  SCAM: 'scam',
  BROKEN_LINK: 'broken_link',
  OWNER_REMOVAL: 'owner_removal',
  INAPPROPRIATE: 'inappropriate',
  DUPLICATE: 'duplicate',
  OTHER: 'other'
};

// Report type labels in English
export const REPORT_TYPE_LABELS = {
  [REPORT_TYPES.SPAM]: 'Spam',
  [REPORT_TYPES.SCAM]: 'Scam/Fraud',
  [REPORT_TYPES.BROKEN_LINK]: 'Broken Link',
  [REPORT_TYPES.OWNER_REMOVAL]: 'I am the owner and want to remove this',
  [REPORT_TYPES.INAPPROPRIATE]: 'Inappropriate Content',
  [REPORT_TYPES.DUPLICATE]: 'Duplicate Listing',
  [REPORT_TYPES.OTHER]: 'Other'
};

// Initialize reports system
export async function initializeReports(auth) {
  if (!auth || !auth.currentUser) {
    console.log('❌ User not authenticated, reports disabled');
    return;
  }

  console.log('🚨 Initializing reports system...');
  // Reports system is ready when user is authenticated
  console.log('✅ Reports system initialized');
}

// Create a new report
export async function createReport(auth, listingId, reportType, description, listingData = {}) {
  if (!auth || !auth.currentUser) {
    console.log('❌ User not authenticated, cannot create report');
    return false;
  }

  try {
    console.log(`🚨 Creating report for listing ${listingId}...`);
    console.log('📋 Report data:', { reportType, description, listingData });
    console.log('📋 Listing title:', listingData.title);
    console.log('📋 Listing link:', listingData.link);
    console.log('📋 Listing price:', listingData.price);
    console.log('📋 Listing zone:', listingData.zone);
    
    const db = getFirestore();
    const currentUser = auth.currentUser;
    
    // Create report document
    const reportData = {
      userId: currentUser.uid,
      userEmail: currentUser.email,
      userDisplayName: currentUser.displayName || 'Anonymous',
      listingId: listingId,
      listingUrl: listingData.link || listingData.url || '',
      listingTitle: listingData.title || 'Untitled',
      listingPrice: listingData.price || 'N/A',
      listingZone: listingData.zone || 'N/A',
      reportType: reportType,
      description: description,
      status: 'pending',
      createdAt: new Date().toISOString(),
      reviewedAt: null,
      reviewerNotes: null
    };
    
    // Add to Firestore
    const reportRef = await addDoc(collection(db, 'reports'), reportData);
    console.log(`✅ Report created with ID: ${reportRef.id}`);
    
    // Log report creation (handled by Firebase Functions)
    console.log('📝 Report saved to Firestore, Firebase Function will log it');
    
    return true;
  } catch (error) {
    console.error('❌ Error creating report:', error);
    return false;
  }
}





// Handle report button click
export async function handleReportClick(auth, listingId, listingDataEncoded = '{}') {
  if (!auth || !auth.currentUser) {
    console.log('❌ User not authenticated, showing login modal');
    // Show login modal or redirect to login
    if (typeof window.showAuthModal === 'function') {
      window.showAuthModal();
    }
    return;
  }

  console.log(`🚨 Report button clicked for listing: ${listingId}`);
  console.log('📋 Encoded listing data:', listingDataEncoded);
  
  // Decode and parse listing data from encoded JSON string
  let listingData = {};
  try {
    const decodedData = decodeURIComponent(listingDataEncoded);
    console.log('📋 Decoded listing data:', decodedData);
    listingData = JSON.parse(decodedData);
    console.log('📋 Listing data parsed successfully:', listingData);
  } catch (error) {
    console.error('❌ Error parsing listing data:', error);
    console.error('❌ Encoded data was:', listingDataEncoded);
    listingData = {};
  }
  
  // Show report modal
  showReportModal(listingId, listingData);
}

// Show report modal
function showReportModal(listingId, listingData) {
  // Create modal HTML
  const modalHTML = `
    <div id="report-modal" class="modal-overlay" data-listing-data='${JSON.stringify(listingData)}'>
      <div class="modal-content report-modal">
        <div class="modal-header">
          <h3>🚨 Report Listing</h3>
          <button class="modal-close" onclick="closeReportModal()">&times;</button>
        </div>
        <div class="modal-body">
          <p class="report-description">Help us keep RoomRadar safe by reporting this listing. Please select a reason and provide additional details.</p>
          
          <div class="form-group">
            <label for="report-type">Report Reason:</label>
            <select id="report-type" class="form-control" required>
              <option value="">Select a reason...</option>
              ${Object.entries(REPORT_TYPE_LABELS).map(([value, label]) => 
                `<option value="${value}">${label}</option>`
              ).join('')}
            </select>
          </div>
          
          <div class="form-group">
            <label for="report-description">Additional Details (optional):</label>
            <textarea id="report-description" class="form-control" rows="4" 
                      placeholder="Please provide any additional details that will help us understand the issue..."></textarea>
          </div>
          
          <div class="form-actions">
            <button class="btn btn-secondary" onclick="closeReportModal()">Cancel</button>
            <button class="btn btn-primary" onclick="submitReport('${listingId}')">Submit Report</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to page
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  
  // Show modal
  setTimeout(() => {
    document.getElementById('report-modal').classList.add('show');
  }, 10);
}

// Close report modal
export function closeReportModal() {
  const modal = document.getElementById('report-modal');
  if (modal) {
    modal.classList.remove('show');
    setTimeout(() => {
      modal.remove();
    }, 300);
  }
}

// Submit report
export async function submitReport(listingId) {
  const reportType = document.getElementById('report-type').value;
  const description = document.getElementById('report-description').value;
  
  if (!reportType) {
    alert('Please select a report reason.');
    return;
  }
  
  try {
    // Get listing data from the modal's data attribute
    const modal = document.getElementById('report-modal');
    const listingDataJson = modal.getAttribute('data-listing-data') || '{}';
    let listingData = {};
    
    console.log('📋 Modal data attribute:', listingDataJson);
    
    try {
      listingData = JSON.parse(listingDataJson);
      console.log('📋 Listing data from modal parsed successfully:', listingData);
    } catch (error) {
      console.error('❌ Error parsing listing data from modal:', error);
      console.error('❌ Modal data was:', listingDataJson);
      // Fallback to DOM extraction
      listingData = getCurrentListingData(listingId);
      console.log('📋 Using fallback DOM data:', listingData);
    }
    
    console.log('📋 Final listing data for report:', listingData);
    
    // Create report
    const success = await createReport(window.auth, listingId, reportType, description, listingData);
    
    if (success) {
      // Close modal
      closeReportModal();
      
      // Show success message
      if (typeof window.showToast === 'function') {
        window.showToast('success', 'Report Submitted', 'Thank you for helping keep RoomRadar safe! 🛡️');
      } else {
        alert('Report submitted successfully! Thank you for helping keep RoomRadar safe! 🛡️');
      }
    } else {
      throw new Error('Failed to create report');
    }
  } catch (error) {
    console.error('❌ Error submitting report:', error);
    
    if (typeof window.showToast === 'function') {
      window.showToast('error', 'Report Error', 'Failed to submit report. Please try again.');
    } else {
      alert('Failed to submit report. Please try again.');
    }
  }
}

// Get current listing data
function getCurrentListingData(listingId) {
  // Try to find the listing in the current page
  const listingElement = document.querySelector(`[data-listing-id="${listingId}"]`);
  if (listingElement) {
    // Extract data from the listing element
    const titleElement = listingElement.querySelector('.listing-title, h3, .card-title');
    const priceElement = listingElement.querySelector('.listing-price, .price, .card-price');
    const zoneElement = listingElement.querySelector('.listing-zone, .zone, .card-zone');
    const linkElement = listingElement.querySelector('a[href*="facebook"]');
    
    return {
      title: titleElement?.textContent?.trim() || 'Untitled',
      price: priceElement?.textContent?.trim() || 'N/A',
      zone: zoneElement?.textContent?.trim() || 'N/A',
      link: linkElement?.href || ''
    };
  }
  
  // Try to find by favorite button data attribute
  const favoriteButton = document.querySelector(`[data-favorite-btn][data-listing-id="${listingId}"]`);
  if (favoriteButton) {
    const cardElement = favoriteButton.closest('.card, .listing-card, [class*="card"]');
    if (cardElement) {
      const titleElement = cardElement.querySelector('.listing-title, h3, .card-title, [class*="title"]');
      const priceElement = cardElement.querySelector('.listing-price, .price, .card-price, [class*="price"]');
      const zoneElement = cardElement.querySelector('.listing-zone, .zone, .card-zone, [class*="zone"]');
      const linkElement = cardElement.querySelector('a[href*="facebook"]');
      
      return {
        title: titleElement?.textContent?.trim() || 'Untitled',
        price: priceElement?.textContent?.trim() || 'N/A',
        zone: zoneElement?.textContent?.trim() || 'N/A',
        link: linkElement?.href || ''
      };
    }
  }
  
  // Fallback to basic data
  return {
    id: listingId,
    title: 'Untitled',
    price: 'N/A',
    zone: 'N/A',
    link: ''
  };
}

// Make functions globally available
window.handleReportClick = handleReportClick;
window.closeReportModal = closeReportModal;
window.submitReport = submitReport;
