class InterviewApp {
    constructor() {
        this.sessionId = null;
        this.userId = 'demo-user'; // In a real app, this would come from authentication
        this.timer = null;
        this.seconds = 0;
        this.isLoading = false;
        this.isEnded = false;

        this.initializeElements();
        this.initializeEventListeners();
        this.startNewSession();
    }

    initializeElements() {
        this.messagesContainer = document.getElementById('messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.advanceStageButton = document.getElementById('advance-stage');
        this.endSessionButton = document.getElementById('end-session');
        this.currentStageElement = document.getElementById('current-stage');
        this.timerElement = document.getElementById('timer');
        this.topicSelect = document.getElementById('topic');
        this.feedbackModal = document.getElementById('feedback-modal');
        this.feedbackContent = document.getElementById('feedback-content');
        this.closeFeedbackButton = document.getElementById('close-feedback');
    }

    initializeEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.advanceStageButton.addEventListener('click', () => this.advanceStage());
        this.endSessionButton.addEventListener('click', () => this.endSession());
        this.closeFeedbackButton.addEventListener('click', () => this.closeFeedback());
    }

    setLoading(isLoading) {
        this.isLoading = isLoading;
        this.sendButton.disabled = isLoading;
        this.advanceStageButton.disabled = isLoading;
        this.endSessionButton.disabled = isLoading;
        this.userInput.disabled = isLoading;
        this.sendButton.textContent = isLoading ? 'Sending...' : 'Send';
    }

    async startNewSession() {
        try {
            this.setLoading(true);
            const topic = this.topicSelect.value;
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic, user_id: this.userId }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const session = await response.json();
            this.sessionId = session.session_id;
            this.startTimer();
            this.addMessage('assistant', 'Welcome to your Cambridge CS interview practice session. I\'ll be your supervisor today. Let\'s begin with some warm-up questions about ' + topic + '.');
        } catch (error) {
            console.error('Error starting session:', error);
            this.showError('Failed to start session. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isLoading) return;

        this.addMessage('user', message);
        this.userInput.value = '';

        try {
            this.setLoading(true);
            const response = await fetch(`/api/sessions/${this.sessionId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const assistantMessage = await response.text();
            this.addMessage('assistant', assistantMessage);
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to send message. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    async advanceStage() {
        if (this.isLoading) return;
        
        try {
            this.setLoading(true);
            const response = await fetch(`/api/sessions/${this.sessionId}/advance`, {
                method: 'POST',
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const newStage = await response.text();
            this.currentStageElement.textContent = newStage.charAt(0).toUpperCase() + newStage.slice(1);
            this.addMessage('assistant', `Moving on to the ${newStage} stage of the interview.`);
        } catch (error) {
            console.error('Error advancing stage:', error);
            this.showError('Failed to advance stage. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    async endSession() {
        if (this.isLoading || this.isEnded) return;
        
        try {
            this.setLoading(true);
            const response = await fetch(`/api/sessions/${this.sessionId}/feedback`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const feedback = await response.text();
            this.showFeedback(feedback);
            this.stopTimer();
            this.isEnded = true;
            
            // Disable input and buttons
            this.userInput.disabled = true;
            this.sendButton.disabled = true;
            this.advanceStageButton.disabled = true;
            this.endSessionButton.disabled = true;
            
            // Show message that session has ended
            this.addMessage('system', 'Interview session has ended. You can review the feedback and generate a report.');
        } catch (error) {
            console.error('Error ending session:', error);
            this.showError('Failed to end session. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        // Replace \n with <br> and preserve whitespace
        const formattedContent = content
            .replace(/\n/g, '<br>')
            .replace(/\s{2,}/g, ' '); // Replace multiple spaces with single space
        
        messageDiv.innerHTML = formattedContent;
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showFeedback(feedback) {
        this.feedbackContent.textContent = feedback;
        this.feedbackModal.style.display = 'block';
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message error';
        errorDiv.textContent = message;
        this.messagesContainer.appendChild(errorDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    closeFeedback() {
        this.feedbackModal.style.display = 'none';
        // Don't start a new session automatically
        // Instead, show a message about how to start a new session
        this.addMessage('system', 'To start a new interview session, please refresh the page.');
    }

    startTimer() {
        this.seconds = 0;
        this.timer = setInterval(() => {
            this.seconds++;
            const minutes = Math.floor(this.seconds / 60);
            const remainingSeconds = this.seconds % 60;
            this.timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new InterviewApp();
});

// Add event listener for the generate report button
document.getElementById('generate-report').addEventListener('click', async () => {
    try {
        // Get the feedback content
        const feedbackContent = document.getElementById('feedback-content').textContent;
        
        if (!feedbackContent) {
            alert('No feedback content available. Please complete an interview session first.');
            return;
        }
        
        // Show loading state
        const button = document.getElementById('generate-report');
        const originalText = button.textContent;
        button.textContent = 'Generating...';
        button.disabled = true;

        // Call the API to generate the filled report
        const response = await fetch('/generate-filled-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ feedback_text: feedbackContent })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate report');
        }

        // Get the blob from the response
        const blob = await response.blob();
        
        if (blob.size === 0) {
            throw new Error('Generated PDF is empty');
        }
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'filled_interview_report.pdf';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error generating report:', error);
        alert(`Failed to generate report: ${error.message}`);
    } finally {
        // Restore button state
        button.textContent = originalText;
        button.disabled = false;
    }
}); 