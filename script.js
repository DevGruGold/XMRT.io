class BoardroomInterface {
    constructor() {
        this.apiUrl = 'https://xmrt-io.onrender.com/api/chat';
        this.agents = {
            'Technical_Agent': { name: 'Technical Agent', color: '#00d4ff', icon: 'fas fa-code' },
            'DAO_Agent': { name: 'DAO Agent', color: '#ff6b6b', icon: 'fas fa-gavel' },
            'Mining_Agent': { name: 'Mining Agent', color: '#ffa500', icon: 'fas fa-pickaxe' },
            'Marketing_Agent': { name: 'Marketing Agent', color: '#ff69b4', icon: 'fas fa-bullhorn' },
            'General_Agent': { name: 'General Agent', color: '#00ff88', icon: 'fas fa-brain' }
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        // Message input
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendMessage');
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Agent seats
        document.querySelectorAll('.agent-seat').forEach(seat => {
            seat.addEventListener('click', () => {
                const agentType = seat.dataset.agent;
                this.showAgentDetails(agentType);
            });
        });

        // Chat controls
        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('exportChat').addEventListener('click', () => {
            this.exportChat();
        });

        // Agent details panel
        document.getElementById('closeDetails').addEventListener('click', () => {
            this.closeAgentDetails();
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const agentSelector = document.getElementById('agentSelector');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Clear input
        messageInput.value = '';

        // Add user message to chat
        this.addMessage('user', 'You', message);

        // Determine target agent
        const selectedAgent = agentSelector.value;
        
        if (selectedAgent === 'all') {
            // Send to all agents
            await this.sendToAllAgents(message);
        } else {
            // Send to specific or auto-routed agent
            await this.sendToAgent(message, selectedAgent);
        }
    }

    async sendToAgent(message, targetAgent = 'auto') {
        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'boardroom_user'
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();

            // Add agent response
            this.addMessage('agent', data.agent_type, data.response);
            
            // Animate agent avatar
            this.animateAgent(data.agent_type);

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('system', 'System', 'Connection error. Please try again.');
        }
    }

    async sendToAllAgents(message) {
        // Show typing for all agents
        this.showTypingIndicator('All agents are discussing...');

        const agentTypes = Object.keys(this.agents);
        const responses = [];

        // Send message and collect responses
        for (const agentType of agentTypes) {
            try {
                const response = await fetch(this.apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: `[${agentType}] ${message}`,
                        user_id: 'boardroom_user'
                    })
                });

                const data = await response.json();
                responses.push(data);
                
                // Animate each agent as they respond
                this.animateAgent(data.agent_type);
                
            } catch (error) {
                console.error(`Error from ${agentType}:`, error);
            }
        }

        this.hideTypingIndicator();

        // Add all responses with slight delays for natural flow
        responses.forEach((data, index) => {
            setTimeout(() => {
                this.addMessage('agent', data.agent_type, data.response);
            }, index * 1000);
        });
    }

    addMessage(type, author, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        let avatarContent = '';
        let authorColor = '#888';
        
        if (type === 'user') {
            avatarContent = '<i class="fas fa-user"></i>';
        } else if (type === 'agent') {
            const agentInfo = this.agents[author];
            if (agentInfo) {
                avatarContent = `<i class="${agentInfo.icon}"></i>`;
                authorColor = agentInfo.color;
            }
        } else {
            avatarContent = '<i class="fas fa-info-circle"></i>';
        }

        // Format content (handle code blocks)
        let formattedContent = content;
        if (content.includes('```')) {
            formattedContent = content.replace(/```(\w+)?\n([\s\S]*?)```/g, 
                '<pre><code>$2</code></pre>');
        }

        messageDiv.innerHTML = `
            <div class="message-avatar" style="color: ${authorColor}; border-color: ${authorColor};">
                ${avatarContent}
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author" style="color: ${authorColor};">${this.agents[author]?.name || author}</span>
                    <span class="message-time">${timestamp}</span>
                </div>
                <div class="message-text">${formattedContent}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator(customText = null) {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <span>${customText || 'Agent is thinking'}</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    animateAgent(agentType) {
        const agentSeat = document.querySelector(`[data-agent="${agentType}"]`);
        if (agentSeat) {
            const avatar = agentSeat.querySelector('.agent-avatar');
            avatar.classList.add('active');
            
            setTimeout(() => {
                avatar.classList.remove('active');
            }, 2000);
        }
    }

    showAgentDetails(agentType) {
        const agentInfo = this.agents[agentType];
        const detailsPanel = document.getElementById('agentDetails');
        const detailsTitle = document.getElementById('detailsTitle');
        const detailsContent = document.getElementById('detailsContent');
        
        detailsTitle.textContent = agentInfo.name;
        
        // Get agent-specific details
        let capabilities = '';
        switch(agentType) {
            case 'Technical_Agent':
                capabilities = `
                    <h4>Capabilities:</h4>
                    <ul>
                        <li>Code generation and debugging</li>
                        <li>API development and integration</li>
                        <li>System architecture design</li>
                        <li>Technical documentation</li>
                    </ul>
                    <h4>Specialties:</h4>
                    <p>JavaScript, Python, Smart Contracts, RESTful APIs</p>
                `;
                break;
            case 'DAO_Agent':
                capabilities = `
                    <h4>Capabilities:</h4>
                    <ul>
                        <li>Governance proposal management</li>
                        <li>Voting system coordination</li>
                        <li>Treasury operations</li>
                        <li>Community consensus building</li>
                    </ul>
                    <h4>Specialties:</h4>
                    <p>Decentralized governance, Smart contract voting, Community management</p>
                `;
                break;
            case 'Mining_Agent':
                capabilities = `
                    <h4>Capabilities:</h4>
                    <ul>
                        <li>Mining operation optimization</li>
                        <li>Hash rate management</li>
                        <li>Pool coordination</li>
                        <li>Leaderboard tracking</li>
                    </ul>
                    <h4>Specialties:</h4>
                    <p>Mining algorithms, Performance optimization, Reward distribution</p>
                `;
                break;
            case 'Marketing_Agent':
                capabilities = `
                    <h4>Capabilities:</h4>
                    <ul>
                        <li>Content creation and strategy</li>
                        <li>Campaign management</li>
                        <li>User acquisition</li>
                        <li>Brand development</li>
                    </ul>
                    <h4>Specialties:</h4>
                    <p>Social media marketing, Content strategy, Community growth</p>
                `;
                break;
            case 'General_Agent':
                capabilities = `
                    <h4>Capabilities:</h4>
                    <ul>
                        <li>General assistance and coordination</li>
                        <li>Multi-domain problem solving</li>
                        <li>Information synthesis</li>
                        <li>Agent coordination</li>
                    </ul>
                    <h4>Specialties:</h4>
                    <p>Cross-functional support, Problem analysis, Strategic planning</p>
                `;
                break;
        }
        
        detailsContent.innerHTML = capabilities;
        detailsPanel.classList.add('open');
    }

    closeAgentDetails() {
        document.getElementById('agentDetails').classList.remove('open');
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        this.showWelcomeMessage();
    }

    exportChat() {
        const messages = document.querySelectorAll('.message');
        let chatLog = 'XMRT.io Boardroom Chat Export\n';
        chatLog += '=' + '='.repeat(40) + '\n\n';
        
        messages.forEach(message => {
            const author = message.querySelector('.message-author')?.textContent || 'System';
            const time = message.querySelector('.message-time')?.textContent || '';
            const text = message.querySelector('.message-text')?.textContent || '';
            
            chatLog += `[${time}] ${author}: ${text}\n\n`;
        });
        
        const blob = new Blob([chatLog], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `xmrt-boardroom-chat-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showWelcomeMessage() {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'system-message';
        welcomeDiv.innerHTML = `
            <i class="fas fa-info-circle"></i>
            Welcome to the XMRT.io AI Boardroom. All agents are online and ready to collaborate.
        `;
        chatMessages.appendChild(welcomeDiv);
    }
}

// Initialize the boardroom interface
document.addEventListener('DOMContentLoaded', () => {
    new BoardroomInterface();
});