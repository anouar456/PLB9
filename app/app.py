<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DURASIA - Monitoring Photovoltaïque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        'serif': ['Playfair Display', 'serif'],
                        'sans': ['Inter', 'sans-serif'],
                    },
                    colors: {
                        'solar': {
                            50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 300: '#86efac',
                            400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d',
                            800: '#166534', 900: '#14532d',
                        },
                        'sun': {
                            50: '#fffbeb', 100: '#fef3c7', 200: '#fde68a', 300: '#fcd34d',
                            400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309',
                            800: '#92400e', 900: '#78350f',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #f0fdf4 0%, #fffbeb 50%, #dcfce7 100%); min-height: 100vh; overflow-x: hidden; }
        .bg-particles { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; overflow: hidden; }
        .particle { position: absolute; border-radius: 50%; background: radial-gradient(circle, rgba(251,191,36,0.3) 0%, transparent 70%); animation: float 20s infinite ease-in-out; }
        @keyframes float { 0%,100%{transform:translateY(0) translateX(0) scale(1);opacity:0.3;} 33%{transform:translateY(-30px) translateX(20px) scale(1.1);opacity:0.5;} 66%{transform:translateY(20px) translateX(-15px) scale(0.9);opacity:0.2;} }
        .glass { background: rgba(255,255,255,0.75); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.5); }
        .glass-dark { background: rgba(20,83,45,0.9); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); }
        .solar-glow { box-shadow: 0 0 30px rgba(251,191,36,0.3), 0 0 60px rgba(34,197,94,0.1); }
        .card-hover { transition: all 0.4s cubic-bezier(0.4,0,0.2,1); }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(20,83,45,0.15); }
        .sidebar { transform: translateX(-100%); transition: transform 0.4s cubic-bezier(0.4,0,0.2,1); }
        .sidebar.open { transform: translateX(0); }
        .chatbot-window { transform: scale(0.9) translateY(20px); opacity: 0; pointer-events: none; transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.4,0,0.2,1); display: flex; flex-direction: column; min-width: 300px; }
        .chatbot-window.open { transform: scale(1) translateY(0); opacity: 1; pointer-events: all; }
        /* Quand déplacé à la main : désactive le transform d'animation */
        .chatbot-window.cb-dragged { transition: opacity 0.25s ease !important; transform: none !important; }
        .chatbot-window.cb-dragged.open { transform: none !important; opacity: 1; }
        /* Plein écran */
        .chatbot-window.cb-fullscreen { top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important; width: 100vw !important; border-radius: 0 !important; transform: none !important; }
        /* Poignée de déplacement */
        #chatbotHeader { cursor: grab; user-select: none; }
        #chatbotHeader:active { cursor: grabbing; }
        /* Poignée de redimensionnement */
        #chatResizeHandle { position: absolute; bottom: 0; right: 0; width: 20px; height: 20px; cursor: se-resize; opacity: 0; transition: opacity 0.2s; z-index: 20; }
        #chatbotWindow:hover #chatResizeHandle { opacity: 1; }
        #chatResizeHandle::before, #chatResizeHandle::after { content:''; position:absolute; background: rgba(20,83,45,0.4); border-radius:1px; }
        #chatResizeHandle::before { width:10px; height:2px; bottom:6px; right:3px; }
        #chatResizeHandle::after  { width:2px; height:10px; bottom:3px; right:6px; }
        /* Grip dots */
        #chatResizeHandle .grip { position:absolute; bottom:2px; right:2px; display:grid; grid-template-columns:repeat(3,4px); gap:2px; }
        #chatResizeHandle .grip span { width:2px; height:2px; border-radius:50%; background:rgba(20,83,45,0.5); display:block; }
        /* Zone messages flexible */
        #chatMessages { overflow-y: auto; }
        .modal-overlay { opacity: 0; pointer-events: none; transition: opacity 0.3s ease; }
        .modal-overlay.open { opacity: 1; pointer-events: all; }
        .modal-content { transform: scale(0.95) translateY(10px); transition: transform 0.3s ease; }
        .modal-overlay.open .modal-content { transform: scale(1) translateY(0); }
        .value-animate { transition: color 0.3s ease; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(20,83,45,0.3); border-radius: 3px; }
        @keyframes pulse-ring { 0%{transform:scale(0.8);opacity:1;} 100%{transform:scale(2);opacity:0;} }
        .live-dot::before { content:''; position:absolute; inset:-4px; border-radius:50%; border:2px solid #22c55e; animation: pulse-ring 2s infinite; }
        @keyframes scan { 0%{top:0;} 50%{top:100%;} 100%{top:0;} }
        .scanner-line { animation: scan 2s infinite linear; }
        .rec-badge { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); position: relative; overflow: hidden; }
        .rec-badge::after { content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.2) 50%, transparent 70%); animation: shimmer 3s infinite; }
        @keyframes shimmer { 0%{transform:translateX(-100%) rotate(45deg);} 100%{transform:translateX(100%) rotate(45deg);} }
        .weather-icon { animation: weather-float 3s ease-in-out infinite; }
        @keyframes weather-float { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-5px);} }
        .typing-dot { animation: typing 1.4s infinite ease-in-out both; }
        .typing-dot:nth-child(1){animation-delay:-0.32s;} .typing-dot:nth-child(2){animation-delay:-0.16s;}
        @keyframes typing { 0%,80%,100%{transform:scale(0);} 40%{transform:scale(1);} }
        .login-bg { background-image: url('https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80'); background-size: cover; background-position: center; }
        .login-bg::before { content:''; position:absolute; inset:0; background: linear-gradient(135deg, rgba(20,83,45,0.88) 0%, rgba(180,83,9,0.75) 100%); }
    </style>

<body>
    <div class="bg-particles" id="particles"></div>

    <div id="loginScreen" class="fixed inset-0 login-bg flex items-center justify-center z-50">
        <div class="relative z-10 w-full max-w-md px-6">
            <div class="text-center mb-10">
                <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 mb-6 solar-glow">
                    <i class="fas fa-sun text-4xl text-sun-300"></i>
                </div>
                <h1 class="font-serif text-4xl font-bold text-white mb-2 tracking-wide">DURASIA</h1>
                <p class="text-white/70 text-sm tracking-widest uppercase">Système Photovoltaïque Intelligent</p>
            </div>
            <div class="glass rounded-3xl p-8 shadow-2xl">
                <div class="flex mb-6 bg-white/10 rounded-xl p-1">
                    <button onclick="switchLoginTab('id')" id="tabId" class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all bg-white text-solar-900 shadow-sm">
                        <i class="fas fa-id-card mr-2"></i>ID Système
                    </button>
                    <button onclick="switchLoginTab('qr')" id="tabQr" class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all text-white/70 hover:text-white">
                        <i class="fas fa-qrcode mr-2"></i>Scan QR
                    </button>
                </div>
                <div id="idPanel" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-solar-800 mb-2">Identifiant Système</label>
                        <div class="relative">
                            <i class="fas fa-microchip absolute left-4 top-1/2 -translate-y-1/2 text-solar-500"></i>
                            <input type="text" id="systemId" placeholder="DUR-2024-001" class="w-full pl-12 pr-4 py-3.5 rounded-xl bg-white/50 border border-solar-200 focus:border-sun-400 focus:ring-2 focus:ring-sun-200 outline-none transition-all text-solar-900 placeholder-solar-400">
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-solar-800 mb-2">Mot de passe</label>
                        <div class="relative">
                            <i class="fas fa-lock absolute left-4 top-1/2 -translate-y-1/2 text-solar-500"></i>
                            <input type="password" id="password" placeholder="••••••••" class="w-full pl-12 pr-4 py-3.5 rounded-xl bg-white/50 border border-solar-200 focus:border-sun-400 focus:ring-2 focus:ring-sun-200 outline-none transition-all text-solar-900 placeholder-solar-400">
                        </div>
                    </div>
                    <button onclick="login()" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-solar-600 to-sun-600 text-white font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all active:scale-[0.98]">
                        <i class="fas fa-sign-in-alt mr-2"></i>Accéder au Système
                    </button>
                </div>
                <div id="qrPanel" class="hidden space-y-4">
                    <div class="relative w-48 h-48 mx-auto bg-white rounded-2xl overflow-hidden border-2 border-solar-200">
                        <div class="absolute inset-0 flex items-center justify-center">
                            <i class="fas fa-qrcode text-6xl text-solar-300"></i>
                        </div>
                        <div class="scanner-line absolute left-0 right-0 h-0.5 bg-sun-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]"></div>
                        <div class="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-sun-500"></div>
                        <div class="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-sun-500"></div>
                        <div class="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-sun-500"></div>
                        <div class="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-sun-500"></div>
                    </div>
                    <p class="text-center text-sm text-solar-600">Placez le QR code dans le cadre</p>
                    <button onclick="simulateQrScan()" class="w-full py-3 rounded-xl bg-solar-100 text-solar-700 font-medium hover:bg-solar-200 transition-all">
                        <i class="fas fa-camera mr-2"></i>Simuler Scan
                    </button>
                </div>
            </div>
            <p class="text-center text-white/50 text-xs mt-6">© 2024 DURASIA Project — Maintenance PV Intelligente</p>
        </div>
    </div>


    <!-- ==================== ADVANCED MODAL ==================== -->
    <div id="advancedModal" class="modal-overlay fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" onclick="closeAdvancedModal()"></div>
        <div class="modal-content relative glass rounded-3xl w-full max-w-6xl max-h-[90vh] overflow-hidden shadow-2xl">
            <div class="flex items-center justify-between p-6 border-b border-solar-100">
                <div class="flex items-center gap-4">
                    <button onclick="closeAdvancedModal()" class="w-10 h-10 rounded-xl bg-solar-50 hover:bg-solar-100 flex items-center justify-center transition-all">
                        <i class="fas fa-arrow-left text-solar-600"></i>
                    </button>
                    <div>
                        <h2 id="modalTitle" class="font-serif text-2xl font-bold text-solar-900">Paramètres Avancés</h2>
                        <p id="modalSubtitle" class="text-sm text-solar-500">Analyse détaillée des données</p>
                    </div>
                </div>
                <div class="flex gap-2">
                    <select id="timeRange" onchange="updateCharts()" class="px-4 py-2 rounded-xl bg-solar-50 border border-solar-200 text-sm text-solar-700 outline-none focus:border-sun-400">
                        <option value="24h">24 Heures</option>
                        <option value="7d">7 Jours</option>
                        <option value="30d">30 Jours</option>
                        <option value="1y">1 An</option>
                    </select>
                    <button onclick="exportData()" class="px-4 py-2 rounded-xl bg-solar-600 text-white text-sm font-medium hover:bg-solar-700 transition-all">
                        <i class="fas fa-download mr-2"></i>Exporter
                    </button>
                </div>
            </div>
            <div class="p-6 overflow-y-auto max-h-[calc(90vh-100px)]" id="modalContent">
                <!-- Dynamic content -->
            </div>
        </div>
    </div>


    <!-- ==================== SIDEBAR ==================== -->
    <div id="sidebarOverlay" onclick="toggleSidebar()" class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 opacity-0 pointer-events-none transition-opacity duration-300"></div>
    <aside id="sidebar" class="sidebar fixed left-0 top-0 h-full w-80 glass-dark z-50 text-white overflow-y-auto">
        <div class="p-6">
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-sun-500/20 flex items-center justify-center">
                        <i class="fas fa-sun text-sun-400 text-lg"></i>
                    </div>
                    <div>
                        <h2 class="font-serif font-bold text-lg">DURASIA</h2>
                        <p class="text-xs text-white/50">Paramètres Avancés</p>
                    </div>
                </div>
                <button onclick="toggleSidebar()" class="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all">
                    <i class="fas fa-times text-sm"></i>
                </button>
            </div>
            <nav class="space-y-2">
                <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl bg-sun-500/20 text-sun-300 border border-sun-500/30">
                    <i class="fas fa-tachometer-alt w-5"></i><span class="font-medium">Tableau de Bord</span>
                </a>
                <a href="#" onclick="openAdvancedModal('production')" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white">
                    <i class="fas fa-chart-line w-5"></i><span>Historique Production</span>
                </a>
                <a href="#" onclick="openAdvancedModal('sensors')" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white">
                    <i class="fas fa-microchip w-5"></i><span>Données Capteurs</span>
                </a>
                <a href="#" onclick="openAdvancedModal('weather')" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white">
                    <i class="fas fa-cloud-sun w-5"></i><span>Prévisions Météo</span>
                </a>
                <a href="#" onclick="openAdvancedModal('prediction')" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white">
                    <i class="fas fa-brain w-5"></i><span>Prédiction IA Production</span>
                </a>
                <div class="border-t border-white/10 my-4"></div>
                <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white">
                    <i class="fas fa-bell w-5"></i><span>Alertes</span><span class="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">3</span>
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white">
                    <i class="fas fa-cog w-5"></i><span>Configuration</span>
                </a>
                <a href="#" onclick="logout()" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-red-500/20 transition-all text-red-300">
                    <i class="fas fa-sign-out-alt w-5"></i><span>Déconnexion</span>
                </a>
            </nav>
            <div class="mt-8 p-4 rounded-2xl bg-white/5 border border-white/10">
                <div class="flex items-center gap-3 mb-3">
                    <div class="w-10 h-10 rounded-full bg-solar-500/30 flex items-center justify-center">
                        <i class="fas fa-user text-solar-300"></i>
                    </div>
                    <div>
                        <p class="font-medium text-sm">Technicien PV</p>
                        <p class="text-xs text-white/50">Système DUR-2024-001</p>
                    </div>
                </div>
                <div class="flex items-center gap-2 text-xs text-white/50">
                    <div class="w-2 h-2 rounded-full bg-green-400 relative"><div class="absolute inset-0 rounded-full bg-green-400 animate-ping"></div></div>
                    En ligne — Dernière sync: il y a 2 min
                </div>
            </div>
        </div>
    </aside>


    <!-- ==================== CHATBOT ==================== -->
    <button id="chatbotToggle" onclick="toggleChatbot()" class="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl bg-gradient-to-br from-solar-600 to-sun-500 text-white shadow-2xl shadow-solar-500/40 flex items-center justify-center hover:scale-110 transition-all">
        <i class="fas fa-robot text-xl"></i>
    </button>
    <div id="chatbotWindow" class="chatbot-window fixed bottom-24 right-6 z-50 glass rounded-3xl shadow-2xl border border-solar-100" style="width:384px;">
        <!-- Header (drag handle) -->
        <div id="chatbotHeader" class="glass-dark p-4 flex items-center justify-between rounded-t-3xl flex-shrink-0">
            <div class="flex items-center gap-2">
                <!-- Grip icon -->
                <div class="flex flex-col gap-[3px] opacity-40 mr-1 flex-shrink-0">
                    <div class="flex gap-[3px]"><div class="w-1 h-1 rounded-full bg-white"></div><div class="w-1 h-1 rounded-full bg-white"></div></div>
                    <div class="flex gap-[3px]"><div class="w-1 h-1 rounded-full bg-white"></div><div class="w-1 h-1 rounded-full bg-white"></div></div>
                    <div class="flex gap-[3px]"><div class="w-1 h-1 rounded-full bg-white"></div><div class="w-1 h-1 rounded-full bg-white"></div></div>
                </div>
                <div class="w-9 h-9 rounded-xl bg-sun-500/20 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-sun-400"></i>
                </div>
                <div>
                    <p class="font-semibold text-white text-sm">Assistant DURASIA</p>
                    <p class="text-xs text-white/50">IA Photovoltaïque</p>
                </div>
            </div>
            <div class="flex items-center gap-1">
                <!-- Bouton plein écran -->
                <button id="fullscreenBtn" onclick="toggleChatbotFullscreen(event)" title="Plein écran"
                    class="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/25 flex items-center justify-center transition-all">
                    <i id="fullscreenIcon" class="fas fa-expand text-white text-xs"></i>
                </button>
                <!-- Bouton fermer -->
                <button onclick="toggleChatbot()" title="Fermer"
                    class="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/25 flex items-center justify-center transition-all">
                    <i class="fas fa-times text-white text-sm"></i>
                </button>
            </div>
        </div>
        <!-- Messages -->
        <div id="chatMessages" class="p-4 space-y-3 bg-white/80" style="height:288px;">
            <div class="flex gap-3">
                <div class="w-8 h-8 rounded-lg bg-solar-100 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-solar-600 text-xs"></i>
                </div>
                <div class="bg-solar-50 rounded-2xl rounded-tl-sm p-3 max-w-[80%]">
                    <p class="text-sm text-solar-800 leading-relaxed">Bonjour ! Je suis votre assistant DURASIA. Posez-moi des questions sur votre système photovoltaïque.</p>
                    <span class="text-xs text-solar-400 mt-1 block">Maintenant</span>
                </div>
            </div>
        </div>
        <!-- Zone de saisie -->
        <div class="p-3 bg-white/90 border-t border-solar-100 rounded-b-3xl flex-shrink-0">
            <div class="flex gap-2 mb-3 flex-wrap">
                <button onclick="sendQuickMessage('Etat du systeme')" class="text-xs px-3 py-1.5 rounded-full bg-solar-100 text-solar-700 hover:bg-solar-200 transition-all">État système</button>
                <button onclick="sendQuickMessage('Production energie')" class="text-xs px-3 py-1.5 rounded-full bg-solar-100 text-solar-700 hover:bg-solar-200 transition-all">Production</button>
                <button onclick="sendQuickMessage('Maintenance nettoyage')" class="text-xs px-3 py-1.5 rounded-full bg-solar-100 text-solar-700 hover:bg-solar-200 transition-all">Maintenance</button>
                <button onclick="sendQuickMessage('Prevision demain')" class="text-xs px-3 py-1.5 rounded-full bg-solar-100 text-solar-700 hover:bg-solar-200 transition-all">Prévisions</button>
            </div>
            <!-- Image preview zone -->
            <div id="imagePreviewZone" class="hidden mb-2 relative">
                <div class="relative inline-block">
                    <img id="imagePreview" src="" alt="Aperçu" class="h-20 rounded-xl border-2 border-sun-300 object-cover shadow-sm">
                    <button onclick="clearImage()" class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center shadow-md hover:bg-red-600 transition-all">
                        <i class="fas fa-times text-xs"></i>
                    </button>
                </div>
                <p class="text-xs text-solar-500 mt-1"><i class="fas fa-image mr-1 text-sun-500"></i>Image prête à envoyer</p>
            </div>
            <!-- Input row -->
            <div class="flex gap-2">
                <input id="chatInput" type="text" placeholder="Posez votre question..." onkeypress="if(event.key==='Enter')sendMessage()"
                    class="flex-1 px-4 py-2.5 rounded-xl bg-solar-50 border border-solar-200 text-sm text-solar-900 outline-none focus:border-sun-400 focus:ring-2 focus:ring-sun-100 placeholder-solar-400 transition-all">
                <input id="imageFileInput" type="file" accept="image/*" capture="environment" class="hidden" onchange="handleImageSelected(event)">
                <button id="cameraBtn" onclick="document.getElementById('imageFileInput').click()" title="Envoyer une photo" class="w-10 h-10 rounded-xl bg-sun-100 text-sun-600 flex items-center justify-center hover:bg-sun-200 transition-all border border-sun-200">
                    <i class="fas fa-camera text-sm"></i>
                </button>
                <button onclick="sendMessage()" class="w-10 h-10 rounded-xl bg-solar-600 text-white flex items-center justify-center hover:bg-solar-700 transition-all">
                    <i class="fas fa-paper-plane text-sm"></i>
                </button>
            </div>
        </div>
        <!-- Poignée de redimensionnement (coin bas-droit) -->
        <div id="chatResizeHandle" title="Redimensionner">
            <div class="grip">
                <span></span><span></span><span></span>
                <span></span><span></span><span></span>
                <span></span><span></span><span></span>
            </div>
        </div>
    </div>

    <!-- ==================== MAIN DASHBOARD ==================== -->
    <div id="dashboard" class="hidden min-h-screen">
        <!-- Top Bar -->
        <header class="glass sticky top-0 z-30 border-b border-solar-100/50">
            <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <button onclick="toggleSidebar()" class="w-10 h-10 rounded-xl bg-solar-50 hover:bg-solar-100 flex items-center justify-center transition-all group">
                        <i class="fas fa-bars text-solar-600 group-hover:text-solar-800"></i>
                    </button>
                    <div class="hidden md:flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-sun-400 to-solar-500 flex items-center justify-center shadow-lg shadow-solar-200">
                            <i class="fas fa-sun text-white text-lg"></i>
                        </div>
                        <div>
                            <h1 class="font-serif text-xl font-bold text-solar-900 leading-tight">DURASIA</h1>
                            <p class="text-xs text-solar-500 tracking-wider">PHOTOVOLTAÏQUE INTELLIGENT</p>
                        </div>
                    </div>
                </div>
                <div class="flex items-center gap-4">
                    <div class="hidden lg:flex items-center gap-3 px-4 py-2 rounded-xl bg-solar-50 border border-solar-100">
                        <i class="fas fa-map-marker-alt text-sun-500"></i>
                        <span class="text-sm text-solar-700 font-medium">Béni Mellal, Maroc</span>
                        <span class="text-xs text-solar-400">32.3°N, 6.4°W</span>
                    </div>
                    <div class="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/60 border border-solar-100">
                        <div class="w-2 h-2 rounded-full bg-green-500 relative">
                            <div class="absolute inset-0 rounded-full bg-green-500 animate-ping opacity-75"></div>
                        </div>
                        <span class="text-sm text-solar-700 font-medium">Système Actif</span>
                    </div>
                    <button onclick="logout()" class="w-10 h-10 rounded-xl bg-solar-50 hover:bg-red-50 flex items-center justify-center transition-all group" title="Déconnexion">
                        <i class="fas fa-sign-out-alt text-solar-400 group-hover:text-red-500 transition-colors"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- AI Recommendation Banner -->
        <div class="max-w-7xl mx-auto px-6 mt-6">
            <div class="rec-badge rounded-2xl p-5 text-white shadow-lg shadow-sun-200/50 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
                <div class="relative flex flex-col md:flex-row md:items-center gap-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
                            <i class="fas fa-robot text-2xl"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full uppercase tracking-wider">IA Recommandation</span>
                                <span class="text-xs opacity-70">il y a 3 min</span>
                            </div>
                            <p id="aiRecommendation" class="font-medium text-sm md:text-base leading-relaxed">
                                Les conditions actuelles sont optimales pour la production. Irradiance élevée (892 W/m²) et température modérée du panneau (42°C). 
                                Aucune maintenance immédiate requise. Prévision de pic de production à 14h30.
                            </p>
                        </div>
                    </div>
                    <button onclick="openAdvancedModal('prediction')" class="md:ml-auto px-5 py-2.5 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-sm text-sm font-semibold transition-all whitespace-nowrap border border-white/20">
                        <i class="fas fa-chart-bar mr-2"></i>Voir les Prévisions
                    </button>
                </div>
            </div>
        </div>

        <!-- Main Grid -->
        <main class="max-w-7xl mx-auto px-6 py-6 pb-32">
            <!-- Weather Section -->
            <div class="mb-8">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="font-serif text-xl font-bold text-solar-900 flex items-center gap-2">
                        <i class="fas fa-cloud-sun text-sun-500"></i> Conditions Météorologiques
                    </h2>
                    <span class="text-sm text-solar-500 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-green-500 live-dot relative"></span>
                        Temps réel
                    </span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="glass rounded-2xl p-5 card-hover border-l-4 border-sun-400">
                        <div class="flex items-start justify-between mb-3">
                            <div class="w-10 h-10 rounded-xl bg-sun-100 flex items-center justify-center weather-icon">
                                <i class="fas fa-temperature-high text-sun-600 text-lg"></i>
                            </div>
                            <span class="text-xs font-medium text-solar-500 bg-solar-50 px-2 py-1 rounded-lg">Ambiante</span>
                        </div>
                        <p class="text-3xl font-bold text-solar-900 font-serif">28.5<span class="text-lg text-solar-400">°C</span></p>
                        <p class="text-xs text-solar-500 mt-1">Ressenti 31°C</p>
                    </div>
                    <div class="glass rounded-2xl p-5 card-hover border-l-4 border-blue-400">
                        <div class="flex items-start justify-between mb-3">
                            <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center weather-icon">
                                <i class="fas fa-tint text-blue-600 text-lg"></i>
                            </div>
                            <span class="text-xs font-medium text-solar-500 bg-solar-50 px-2 py-1 rounded-lg">Humidité</span>
                        </div>
                        <p class="text-3xl font-bold text-solar-900 font-serif">42<span class="text-lg text-solar-400">%</span></p>
                        <p class="text-xs text-solar-500 mt-1">Baisse prévue -5%</p>
                    </div>
                    <div class="glass rounded-2xl p-5 card-hover border-l-4 border-cyan-400">
                        <div class="flex items-start justify-between mb-3">
                            <div class="w-10 h-10 rounded-xl bg-cyan-100 flex items-center justify-center weather-icon">
                                <i class="fas fa-wind text-cyan-600 text-lg"></i>
                            </div>
                            <span class="text-xs font-medium text-solar-500 bg-solar-50 px-2 py-1 rounded-lg">Vent</span>
                        </div>
                        <p class="text-3xl font-bold text-solar-900 font-serif">12.3<span class="text-lg text-solar-400">km/h</span></p>
                        <p class="text-xs text-solar-500 mt-1">Direction NE</p>
                    </div>
                    <div class="glass rounded-2xl p-5 card-hover border-l-4 border-amber-400">
                        <div class="flex items-start justify-between mb-3">
                            <div class="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center weather-icon">
                                <i class="fas fa-eye text-amber-600 text-lg"></i>
                            </div>
                            <span class="text-xs font-medium text-solar-500 bg-solar-50 px-2 py-1 rounded-lg">Visibilité</span>
                        </div>
                        <p class="text-3xl font-bold text-solar-900 font-serif">10<span class="text-lg text-solar-400">km</span></p>
                        <p class="text-xs text-solar-500 mt-1">Très bonne</p>
                    </div>
                </div>
            </div>

            <!-- Sensor Parameters -->
            <div class="mb-8">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="font-serif text-xl font-bold text-solar-900 flex items-center gap-2">
                        <i class="fas fa-microchip text-solar-600"></i> Paramètres Système (Temps Réel)
                    </h2>
                    <button onclick="openAdvancedModal('sensors')" class="px-4 py-2 rounded-xl bg-solar-100 hover:bg-solar-200 text-solar-700 text-sm font-medium transition-all flex items-center gap-2">
                        <i class="fas fa-expand-alt"></i> Vue Avancée
                    </button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <!-- Irradiance -->
                    <div class="glass rounded-2xl p-5 card-hover relative overflow-hidden group">
                        <div class="absolute -right-6 -top-6 w-24 h-24 bg-sun-400/10 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                        <div class="relative">
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-sun-400 to-orange-500 flex items-center justify-center shadow-lg shadow-sun-200">
                                        <i class="fas fa-sun text-white"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Irradiance Solaire</p>
                                        <p class="text-xs text-solar-400">Capteur pyranomètre</p>
                                    </div>
                                </div>
                                <div class="w-2 h-2 rounded-full bg-green-500 relative live-dot"></div>
                            </div>
                            <div class="flex items-end gap-2 mb-2">
                                <span id="irradianceValue" class="text-4xl font-bold text-solar-900 font-serif value-animate">892</span>
                                <span class="text-sm text-solar-500 mb-1 font-medium">W/m²</span>
                            </div>
                            <div class="w-full bg-solar-100 rounded-full h-2 mb-3 overflow-hidden">
                                <div id="irradianceBar" class="bg-gradient-to-r from-sun-400 to-orange-500 h-full rounded-full transition-all duration-1000" style="width: 89%"></div>
                            </div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-solar-400">0 W/m²</span>
                                <span id="irradianceStatus" class="font-medium text-sun-600 bg-sun-50 px-2 py-0.5 rounded-full">Élevée</span>
                                <span class="text-solar-400">1000 W/m²</span>
                            </div>
                        </div>
                    </div>
                    <!-- Panel Temperature -->
                    <div class="glass rounded-2xl p-5 card-hover relative overflow-hidden group">
                        <div class="absolute -right-6 -top-6 w-24 h-24 bg-red-400/10 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                        <div class="relative">
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-400 to-orange-500 flex items-center justify-center shadow-lg shadow-red-200">
                                        <i class="fas fa-thermometer-half text-white"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Temp. Panneau</p>
                                        <p class="text-xs text-solar-400">Capteur IR</p>
                                    </div>
                                </div>
                                <div class="w-2 h-2 rounded-full bg-green-500 relative live-dot"></div>
                            </div>
                            <div class="flex items-end gap-2 mb-2">
                                <span id="panelTempValue" class="text-4xl font-bold text-solar-900 font-serif value-animate">42.3</span>
                                <span class="text-sm text-solar-500 mb-1 font-medium">°C</span>
                            </div>
                            <div class="w-full bg-solar-100 rounded-full h-2 mb-3 overflow-hidden">
                                <div id="panelTempBar" class="bg-gradient-to-r from-orange-400 to-red-500 h-full rounded-full transition-all duration-1000" style="width: 60%"></div>
                            </div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-solar-400">0°C</span>
                                <span id="panelTempStatus" class="font-medium text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full">Modérée</span>
                                <span class="text-solar-400">80°C</span>
                            </div>
                        </div>
                    </div>
                    <!-- Cooling Humidity -->
                    <div class="glass rounded-2xl p-5 card-hover relative overflow-hidden group">
                        <div class="absolute -right-6 -top-6 w-24 h-24 bg-blue-400/10 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                        <div class="relative">
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-200">
                                        <i class="fas fa-water text-white"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Humidité Refroid.</p>
                                        <p class="text-xs text-solar-400">Capteur hygromètre</p>
                                    </div>
                                </div>
                                <div class="w-2 h-2 rounded-full bg-green-500 relative live-dot"></div>
                            </div>
                            <div class="flex items-end gap-2 mb-2">
                                <span id="coolingHumidityValue" class="text-4xl font-bold text-solar-900 font-serif value-animate">35</span>
                                <span class="text-sm text-solar-500 mb-1 font-medium">%</span>
                            </div>
                            <div class="w-full bg-solar-100 rounded-full h-2 mb-3 overflow-hidden">
                                <div id="coolingHumidityBar" class="bg-gradient-to-r from-blue-400 to-cyan-500 h-full rounded-full transition-all duration-1000" style="width: 35%"></div>
                            </div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-solar-400">0%</span>
                                <span id="coolingHumidityStatus" class="font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Normale</span>
                                <span class="text-solar-400">100%</span>
                            </div>
                        </div>
                    </div>
                    <!-- Dust Percentage -->
                    <div class="glass rounded-2xl p-5 card-hover relative overflow-hidden group">
                        <div class="absolute -right-6 -top-6 w-24 h-24 bg-amber-400/10 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                        <div class="relative">
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-yellow-600 flex items-center justify-center shadow-lg shadow-amber-200">
                                        <i class="fas fa-layer-group text-white"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Taux de Poussière</p>
                                        <p class="text-xs text-solar-400">Capteur optique</p>
                                    </div>
                                </div>
                                <div class="w-2 h-2 rounded-full bg-green-500 relative live-dot"></div>
                            </div>
                            <div class="flex items-end gap-2 mb-2">
                                <span id="dustValue" class="text-4xl font-bold text-solar-900 font-serif value-animate">8.2</span>
                                <span class="text-sm text-solar-500 mb-1 font-medium">%</span>
                            </div>
                            <div class="w-full bg-solar-100 rounded-full h-2 mb-3 overflow-hidden">
                                <div id="dustBar" class="bg-gradient-to-r from-green-400 to-amber-500 h-full rounded-full transition-all duration-1000" style="width: 8.2%"></div>
                            </div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-solar-400">0%</span>
                                <span id="dustStatus" class="font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">Faible</span>
                                <span class="text-solar-400">100%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Production Overview -->
            <div class="mb-8">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="font-serif text-xl font-bold text-solar-900 flex items-center gap-2">
                        <i class="fas fa-bolt text-sun-500"></i> Production Énergétique
                    </h2>
                    <button onclick="openAdvancedModal('production')" class="px-4 py-2 rounded-xl bg-solar-100 hover:bg-solar-200 text-solar-700 text-sm font-medium transition-all flex items-center gap-2">
                        <i class="fas fa-chart-area"></i> Historique Détaillé
                    </button>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div class="lg:col-span-2 glass rounded-2xl p-6 card-hover">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <p class="text-sm font-semibold text-solar-700">Production Journalière</p>
                                <p class="text-xs text-solar-400">Courbe de puissance instantanée</p>
                            </div>
                            <div class="flex gap-2">
                                <span class="text-xs px-3 py-1 rounded-full bg-sun-100 text-sun-700 font-medium">Aujourd'hui</span>
                            </div>
                        </div>
                        <div class="h-64">
                            <canvas id="productionChart"></canvas>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="glass rounded-2xl p-5 card-hover">
                            <div class="flex items-center gap-3 mb-3">
                                <div class="w-10 h-10 rounded-xl bg-sun-100 flex items-center justify-center">
                                    <i class="fas fa-bolt text-sun-600"></i>
                                </div>
                                <div>
                                    <p class="text-xs text-solar-500">Puissance Actuelle</p>
                                    <p id="currentPower" class="text-2xl font-bold text-solar-900 font-serif">4.85<span class="text-sm text-solar-400"> kW</span></p>
                                </div>
                            </div>
                            <div class="flex items-center gap-2 text-xs text-green-600 bg-green-50 px-3 py-2 rounded-lg">
                                <i class="fas fa-arrow-up"></i>
                                <span>+12% vs hier à la même heure</span>
                            </div>
                        </div>
                        <div class="glass rounded-2xl p-5 card-hover">
                            <div class="flex items-center gap-3 mb-3">
                                <div class="w-10 h-10 rounded-xl bg-solar-100 flex items-center justify-center">
                                    <i class="fas fa-calendar-day text-solar-600"></i>
                                </div>
                                <div>
                                    <p class="text-xs text-solar-500">Production Aujourd'hui</p>
                                    <p id="dailyEnergy" class="text-2xl font-bold text-solar-900 font-serif">28.4<span class="text-sm text-solar-400"> kWh</span></p>
                                </div>
                            </div>
                            <div class="flex items-center gap-2 text-xs text-green-600 bg-green-50 px-3 py-2 rounded-lg">
                                <i class="fas fa-arrow-up"></i>
                                <span>Objectif: 32 kWh (89%)</span>
                            </div>
                        </div>
                        <div class="glass rounded-2xl p-5 card-hover">
                            <div class="flex items-center gap-3 mb-3">
                                <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                                    <i class="fas fa-leaf text-blue-600"></i>
                                </div>
                                <div>
                                    <p class="text-xs text-solar-500">CO₂ Évité</p>
                                    <p class="text-2xl font-bold text-solar-900 font-serif">18.6<span class="text-sm text-solar-400"> kg</span></p>
                                </div>
                            </div>
                            <div class="flex items-center gap-2 text-xs text-solar-500 bg-solar-50 px-3 py-2 rounded-lg">
                                <i class="fas fa-tree"></i>
                                <span>Équivalent à 0.9 arbres</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Weather Forecast & Prediction -->
            <div class="mb-8">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="font-serif text-xl font-bold text-solar-900 flex items-center gap-2">
                        <i class="fas fa-cloud-sun-rain text-sun-500"></i> Prévisions & Prédiction IA
                    </h2>
                    <button onclick="openAdvancedModal('weather')" class="px-4 py-2 rounded-xl bg-solar-100 hover:bg-solar-200 text-solar-700 text-sm font-medium transition-all flex items-center gap-2">
                        <i class="fas fa-expand"></i> Vue Détaillée
                    </button>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div class="glass rounded-2xl p-6 card-hover">
                        <div class="flex items-center justify-between mb-4">
                            <p class="text-sm font-semibold text-solar-700">Prévision Météo (5 jours)</p>
                            <span class="text-xs text-solar-400">Source: API Météo</span>
                        </div>
                        <div class="space-y-3" id="weatherForecast">
                            <div class="flex items-center justify-between p-3 rounded-xl bg-solar-50/50 hover:bg-solar-50 transition-all">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-lg bg-sun-100 flex items-center justify-center">
                                        <i class="fas fa-sun text-sun-500"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Aujourd'hui</p>
                                        <p class="text-xs text-solar-400">Ensoleillé</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-bold text-solar-900">32°C</p>
                                    <p class="text-xs text-solar-400">15% pluie</p>
                                </div>
                            </div>
                            <div class="flex items-center justify-between p-3 rounded-xl hover:bg-solar-50 transition-all">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-lg bg-sun-100 flex items-center justify-center">
                                        <i class="fas fa-cloud-sun text-sun-400"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Demain</p>
                                        <p class="text-xs text-solar-400">Partiellement nuageux</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-bold text-solar-900">30°C</p>
                                    <p class="text-xs text-solar-400">20% pluie</p>
                                </div>
                            </div>
                            <div class="flex items-center justify-between p-3 rounded-xl hover:bg-solar-50 transition-all">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                                        <i class="fas fa-cloud text-blue-400"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Mercredi</p>
                                        <p class="text-xs text-solar-400">Nuageux</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-bold text-solar-900">28°C</p>
                                    <p class="text-xs text-solar-400">45% pluie</p>
                                </div>
                            </div>
                            <div class="flex items-center justify-between p-3 rounded-xl hover:bg-solar-50 transition-all">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-lg bg-sun-100 flex items-center justify-center">
                                        <i class="fas fa-sun text-sun-500"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Jeudi</p>
                                        <p class="text-xs text-solar-400">Ensoleillé</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-bold text-solar-900">33°C</p>
                                    <p class="text-xs text-solar-400">5% pluie</p>
                                </div>
                            </div>
                            <div class="flex items-center justify-between p-3 rounded-xl hover:bg-solar-50 transition-all">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                                        <i class="fas fa-wind text-amber-500"></i>
                                    </div>
                                    <div>
                                        <p class="text-sm font-semibold text-solar-800">Vendredi</p>
                                        <p class="text-xs text-solar-400">Venté</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-bold text-solar-900">29°C</p>
                                    <p class="text-xs text-solar-400">10% pluie</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="glass rounded-2xl p-6 card-hover">
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex items-center gap-2">
                                <i class="fas fa-brain text-purple-500"></i>
                                <p class="text-sm font-semibold text-solar-700">Prédiction IA — Pics de Production</p>
                            </div>
                            <span class="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700 font-medium">Modèle LSTM</span>
                        </div>
                        <div class="h-48 mb-4">
                            <canvas id="predictionChart"></canvas>
                        </div>
                        <div class="grid grid-cols-3 gap-3">
                            <div class="text-center p-3 rounded-xl bg-solar-50">
                                <p class="text-xs text-solar-500 mb-1">Pic Prédit</p>
                                <p class="text-lg font-bold text-solar-900 font-serif">5.2<span class="text-xs">kW</span></p>
                                <p class="text-xs text-sun-600">14h30</p>
                            </div>
                            <div class="text-center p-3 rounded-xl bg-solar-50">
                                <p class="text-xs text-solar-500 mb-1">Production Est.</p>
                                <p class="text-lg font-bold text-solar-900 font-serif">31.8<span class="text-xs">kWh</span></p>
                                <p class="text-xs text-green-600">+99% objectif</p>
                            </div>
                            <div class="text-center p-3 rounded-xl bg-solar-50">
                                <p class="text-xs text-solar-500 mb-1">Confiance</p>
                                <p class="text-lg font-bold text-solar-900 font-serif">94<span class="text-xs">%</span></p>
                                <p class="text-xs text-solar-400">Très élevée</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <script>
        // ========== ADVANCED MODAL ==========
        function openAdvancedModal(type) {
            const modal = document.getElementById('advancedModal');
            const title = document.getElementById('modalTitle');
            const subtitle = document.getElementById('modalSubtitle');
            const content = document.getElementById('modalContent');

            modal.classList.add('open');

            if (type === 'sensors') {
                title.textContent = 'Donnees Capteurs Avancees';
                subtitle.textContent = 'Historique et analyses des capteurs du systeme';
                content.innerHTML = `
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div class="glass rounded-2xl p-5">
                            <h3 class="font-semibold text-solar-800 mb-4 flex items-center gap-2"><i class="fas fa-sun text-sun-500"></i> Irradiance Solaire</h3>
                            <div class="h-64"><canvas id="advancedChart1"></canvas></div>
                        </div>
                        <div class="glass rounded-2xl p-5">
                            <h3 class="font-semibold text-solar-800 mb-4 flex items-center gap-2"><i class="fas fa-thermometer-half text-red-500"></i> Temperature Panneau</h3>
                            <div class="h-64"><canvas id="advancedChart2"></canvas></div>
                        </div>
                        <div class="glass rounded-2xl p-5">
                            <h3 class="font-semibold text-solar-800 mb-4 flex items-center gap-2"><i class="fas fa-water text-blue-500"></i> Humidite Refroidissement</h3>
                            <div class="h-64"><canvas id="advancedChart3"></canvas></div>
                        </div>
                        <div class="glass rounded-2xl p-5">
                            <h3 class="font-semibold text-solar-800 mb-4 flex items-center gap-2"><i class="fas fa-layer-group text-amber-500"></i> Taux de Poussiere</h3>
                            <div class="h-64"><canvas id="advancedChart4"></canvas></div>
                        </div>
                    </div>
                    <div class="mt-6 glass rounded-2xl p-5">
                        <h3 class="font-semibold text-solar-800 mb-4">Tableau de Donnees Detailles</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead>
                                    <tr class="border-b border-solar-200">
                                        <th class="text-left py-3 px-4 text-solar-600 font-medium">Heure</th>
                                        <th class="text-left py-3 px-4 text-solar-600 font-medium">Irradiance (W/m2)</th>
                                        <th class="text-left py-3 px-4 text-solar-600 font-medium">Temp. Panneau (C)</th>
                                        <th class="text-left py-3 px-4 text-solar-600 font-medium">Humidite (%)</th>
                                        <th class="text-left py-3 px-4 text-solar-600 font-medium">Poussiere (%)</th>
                                        <th class="text-left py-3 px-4 text-solar-600 font-medium">Statut</th>
                                    </tr>
                                </thead>
                                <tbody id="sensorTableBody"></tbody>
                            </table>
                        </div>
                    </div>
                `;
                setTimeout(() => initAdvancedCharts('sensors'), 100);
            } else if (type === 'production') {
                title.textContent = 'Historique de Production';
                subtitle.textContent = 'Analyse detaillee de la production energetique';
                content.innerHTML = `
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                        <div class="glass rounded-2xl p-5 text-center">
                            <p class="text-xs text-solar-500 mb-1">Production Totale (Mois)</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">847.3<span class="text-sm text-solar-400"> kWh</span></p>
                        </div>
                        <div class="glass rounded-2xl p-5 text-center">
                            <p class="text-xs text-solar-500 mb-1">Rendement Moyen</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">18.4<span class="text-sm text-solar-400"> %</span></p>
                        </div>
                        <div class="glass rounded-2xl p-5 text-center">
                            <p class="text-xs text-solar-500 mb-1">Temps de Fonctionnement</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">312<span class="text-sm text-solar-400"> h</span></p>
                        </div>
                    </div>
                    <div class="glass rounded-2xl p-5 mb-6">
                        <h3 class="font-semibold text-solar-800 mb-4">Courbe de Production — 7 Derniers Jours</h3>
                        <div class="h-72"><canvas id="advancedChartProd"></canvas></div>
                    </div>
                    <div class="glass rounded-2xl p-5">
                        <h3 class="font-semibold text-solar-800 mb-4">Resume Journalier</h3>
                        <div class="grid grid-cols-7 gap-2">
                            ${['Lun','Mar','Mer','Jeu','Ven','Sam','Dim'].map((d,i) => `
                                <div class="text-center p-3 rounded-xl ${i===5?'bg-sun-100 border border-sun-200':'bg-solar-50'} hover:bg-solar-100 transition-all cursor-pointer">
                                    <p class="text-xs text-solar-500 mb-1">${d}</p>
                                    <p class="text-lg font-bold text-solar-900 font-serif">${(25+Math.random()*10).toFixed(1)}</p>
                                    <p class="text-xs text-solar-400">kWh</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                setTimeout(() => initAdvancedCharts('production'), 100);
            } else if (type === 'weather') {
                title.textContent = 'Previsions Meteorologiques';
                subtitle.textContent = 'Donnees meteo detaillees et historique';
                content.innerHTML = `
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div class="glass rounded-2xl p-5">
                            <h3 class="font-semibold text-solar-800 mb-4">Temperature sur 24h</h3>
                            <div class="h-64"><canvas id="advancedChartWeather1"></canvas></div>
                        </div>
                        <div class="glass rounded-2xl p-5">
                            <h3 class="font-semibold text-solar-800 mb-4">Humidite sur 24h</h3>
                            <div class="h-64"><canvas id="advancedChartWeather2"></canvas></div>
                        </div>
                    </div>
                    <div class="mt-6 glass rounded-2xl p-5">
                        <h3 class="font-semibold text-solar-800 mb-4">Previsions 7 Jours Detailles</h3>
                        <div class="grid grid-cols-7 gap-3">
                            ${[
                                {day:'Lun', icon:'fa-sun', temp:'32', cond:'Ensoleille', rain:'5%'},
                                {day:'Mar', icon:'fa-cloud-sun', temp:'30', cond:'Part. nuageux', rain:'20%'},
                                {day:'Mer', icon:'fa-cloud', temp:'28', cond:'Nuageux', rain:'45%'},
                                {day:'Jeu', icon:'fa-sun', temp:'33', cond:'Ensoleille', rain:'5%'},
                                {day:'Ven', icon:'fa-wind', temp:'29', cond:'Vente', rain:'10%'},
                                {day:'Sam', icon:'fa-cloud-sun-rain', temp:'27', cond:'Averses', rain:'60%'},
                                {day:'Dim', icon:'fa-sun', temp:'31', cond:'Ensoleille', rain:'5%'}
                            ].map(w => `
                                <div class="text-center p-4 rounded-2xl bg-solar-50 hover:bg-solar-100 transition-all border border-solar-100">
                                    <p class="text-sm font-semibold text-solar-800 mb-2">${w.day}</p>
                                    <i class="fas ${w.icon} text-2xl text-sun-500 mb-2"></i>
                                    <p class="text-xl font-bold text-solar-900 font-serif">${w.temp}</p>
                                    <p class="text-xs text-solar-500 mt-1">${w.cond}</p>
                                    <p class="text-xs text-blue-500 mt-1"><i class="fas fa-tint mr-1"></i>${w.rain}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                setTimeout(() => initAdvancedCharts('weather'), 100);
            } else if (type === 'prediction') {
                title.textContent = 'Prediction IA — Pics de Production';
                subtitle.textContent = 'Modele de prediction base sur LSTM et donnees meteo';
                content.innerHTML = `
                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
                        <div class="glass rounded-2xl p-5 text-center border-l-4 border-purple-500">
                            <p class="text-xs text-solar-500 mb-1">Precision du Modele</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">94.2<span class="text-sm text-solar-400">%</span></p>
                        </div>
                        <div class="glass rounded-2xl p-5 text-center border-l-4 border-sun-500">
                            <p class="text-xs text-solar-500 mb-1">Pic Predi Aujourd'hui</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">5.2<span class="text-sm text-solar-400">kW</span></p>
                        </div>
                        <div class="glass rounded-2xl p-5 text-center border-l-4 border-green-500">
                            <p class="text-xs text-solar-500 mb-1">Production Est. Jour</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">31.8<span class="text-sm text-solar-400">kWh</span></p>
                        </div>
                        <div class="glass rounded-2xl p-5 text-center border-l-4 border-blue-500">
                            <p class="text-xs text-solar-500 mb-1">Erreur Moyenne</p>
                            <p class="text-3xl font-bold text-solar-900 font-serif">+-3.2<span class="text-sm text-solar-400">%</span></p>
                        </div>
                    </div>
                    <div class="glass rounded-2xl p-5 mb-6">
                        <h3 class="font-semibold text-solar-800 mb-4">Prediction vs Reel — 7 Derniers Jours</h3>
                        <div class="h-80"><canvas id="advancedChartPred"></canvas></div>
                    </div>
                    <div class="glass rounded-2xl p-5">
                        <h3 class="font-semibold text-solar-800 mb-4">Parametres du Modele</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="p-4 rounded-xl bg-solar-50">
                                <p class="text-xs text-solar-500 mb-1">Architecture</p>
                                <p class="font-semibold text-solar-800">LSTM 3 couches</p>
                                <p class="text-xs text-solar-400 mt-1">128, 64, 32 neurones</p>
                            </div>
                            <div class="p-4 rounded-xl bg-solar-50">
                                <p class="text-xs text-solar-500 mb-1">Entrees</p>
                                <p class="font-semibold text-solar-800">12 features</p>
                                <p class="text-xs text-solar-400 mt-1">Irradiance, temp, humidite, vent, historique...</p>
                            </div>
                            <div class="p-4 rounded-xl bg-solar-50">
                                <p class="text-xs text-solar-500 mb-1">Derniere Entrainement</p>
                                <p class="font-semibold text-solar-800">Il y a 2 jours</p>
                                <p class="text-xs text-solar-400 mt-1">10,000 epochs — Dataset 2 ans</p>
                            </div>
                        </div>
                    </div>
                `;
                setTimeout(() => initAdvancedCharts('prediction'), 100);
            }
        }

        function closeAdvancedModal() {
            document.getElementById('advancedModal').classList.remove('open');
        }

        function updateCharts() {
            console.log('Updating charts for range:', document.getElementById('timeRange').value);
        }

        function exportData() {
            alert('Export des donnees en cours... (CSV/PDF)');
        }

        // ========== PARTICLES ==========
        function createParticles() {
            const container = document.getElementById('particles');
            for (let i = 0; i < 15; i++) {
                const p = document.createElement('div');
                p.className = 'particle';
                p.style.width = Math.random() * 200 + 50 + 'px';
                p.style.height = p.style.width;
                p.style.left = Math.random() * 100 + '%';
                p.style.top = Math.random() * 100 + '%';
                p.style.animationDelay = Math.random() * 20 + 's';
                p.style.animationDuration = (15 + Math.random() * 15) + 's';
                container.appendChild(p);
            }
        }
        createParticles();

        // ========== LOGIN ==========
        function switchLoginTab(tab) {
            document.getElementById('tabId').className = tab === 'id' 
                ? 'flex-1 py-2.5 rounded-lg text-sm font-medium transition-all bg-white text-solar-900 shadow-sm'
                : 'flex-1 py-2.5 rounded-lg text-sm font-medium transition-all text-white/70 hover:text-white';
            document.getElementById('tabQr').className = tab === 'qr'
                ? 'flex-1 py-2.5 rounded-lg text-sm font-medium transition-all bg-white text-solar-900 shadow-sm'
                : 'flex-1 py-2.5 rounded-lg text-sm font-medium transition-all text-white/70 hover:text-white';
            document.getElementById('idPanel').classList.toggle('hidden', tab !== 'id');
            document.getElementById('qrPanel').classList.toggle('hidden', tab !== 'qr');
        }

        function simulateQrScan() {
            const btn = event.target.closest('button');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Scan en cours...';
            setTimeout(() => {
                document.getElementById('systemId').value = 'DUR-2024-001';
                login();
            }, 2000);
        }

        function login() {
            const id = document.getElementById('systemId').value;
            if (!id) { alert('Veuillez entrer un identifiant'); return; }
            document.getElementById('loginScreen').style.opacity = '0';
            document.getElementById('loginScreen').style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                document.getElementById('loginScreen').classList.add('hidden');
                document.getElementById('dashboard').classList.remove('hidden');
                initCharts();
                startRealtimeUpdates();
            }, 500);
        }

        function logout() {
            document.getElementById('dashboard').classList.add('hidden');
            document.getElementById('loginScreen').classList.remove('hidden');
            document.getElementById('loginScreen').style.opacity = '1';
            document.getElementById('systemId').value = '';
            document.getElementById('password').value = '';
        }

        // ========== SIDEBAR ==========
        function toggleSidebar() {
            const sb = document.getElementById('sidebar');
            const ov = document.getElementById('sidebarOverlay');
            sb.classList.toggle('open');
            ov.style.opacity = sb.classList.contains('open') ? '1' : '0';
            ov.style.pointerEvents = sb.classList.contains('open') ? 'auto' : 'none';
        }

        // ========== CHATBOT ==========
        const GROQ_API_KEY = "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";
        const GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"; // Llama 4 Scout — vision gratuit sur Groq
        let chatHistory = []; // Historique de conversation pour contexte multi-tour
        let pendingImageBase64 = null;  // Image en attente d'envoi
        let pendingImageMime = "image/jpeg";

        function toggleChatbot() {
            const cw = document.getElementById('chatbotWindow');
            const ct = document.getElementById('chatbotToggle');
            cw.classList.toggle('open');
            ct.style.transform = cw.classList.contains('open') ? 'scale(0)' : 'scale(1)';
        }

        // ===== PLEIN ÉCRAN =====
        function toggleChatbotFullscreen(e) {
            e.stopPropagation();
            const cw   = document.getElementById('chatbotWindow');
            const icon = document.getElementById('fullscreenIcon');
            const msgs = document.getElementById('chatMessages');
            const isFs = cw.classList.contains('cb-fullscreen');

            if (isFs) {
                // Quitter plein écran
                cw.classList.remove('cb-fullscreen');
                icon.className = 'fas fa-expand text-white text-xs';
                msgs.style.height = '288px';
                cw.style.borderRadius = '';
            } else {
                // Activer plein écran
                cw.classList.add('cb-fullscreen', 'cb-dragged');
                icon.className = 'fas fa-compress text-white text-xs';
                // Hauteur = 100vh − header(~65px) − input(~135px)
                msgs.style.height = 'calc(100vh - 200px)';
                cw.style.borderRadius = '0';
            }
            msgs.scrollTop = msgs.scrollHeight;
        }

        // ===== DÉPLACEMENT (DRAG) =====
        (function initChatDrag() {
            const cw = document.getElementById('chatbotWindow');
            const header = document.getElementById('chatbotHeader');
            let dragging = false, sx, sy, sl, st;

            function ensurePositioned() {
                if (!cw.classList.contains('cb-dragged')) {
                    const r = cw.getBoundingClientRect();
                    cw.style.left   = r.left + 'px';
                    cw.style.top    = r.top  + 'px';
                    cw.style.right  = 'auto';
                    cw.style.bottom = 'auto';
                    cw.classList.add('cb-dragged');
                }
            }

            function clamp(val, min, max) { return Math.max(min, Math.min(max, val)); }

            // ---- Mouse ----
            header.addEventListener('mousedown', (e) => {
                if (e.target.closest('button')) return;
                if (cw.classList.contains('cb-fullscreen')) return;
                ensurePositioned();
                dragging = true;
                sx = e.clientX; sy = e.clientY;
                sl = parseInt(cw.style.left) || 0;
                st = parseInt(cw.style.top)  || 0;
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!dragging) return;
                const nx = clamp(sl + e.clientX - sx, 0, window.innerWidth  - cw.offsetWidth);
                const ny = clamp(st + e.clientY - sy, 0, window.innerHeight - cw.offsetHeight);
                cw.style.left = nx + 'px';
                cw.style.top  = ny + 'px';
            });

            document.addEventListener('mouseup', () => { dragging = false; });

            // ---- Touch ----
            header.addEventListener('touchstart', (e) => {
                if (e.target.closest('button')) return;
                if (cw.classList.contains('cb-fullscreen')) return;
                ensurePositioned();
                dragging = true;
                const t = e.touches[0];
                sx = t.clientX; sy = t.clientY;
                sl = parseInt(cw.style.left) || 0;
                st = parseInt(cw.style.top)  || 0;
            }, { passive: true });

            document.addEventListener('touchmove', (e) => {
                if (!dragging) return;
                const t = e.touches[0];
                const nx = clamp(sl + t.clientX - sx, 0, window.innerWidth  - cw.offsetWidth);
                const ny = clamp(st + t.clientY - sy, 0, window.innerHeight - cw.offsetHeight);
                cw.style.left = nx + 'px';
                cw.style.top  = ny + 'px';
            }, { passive: true });

            document.addEventListener('touchend', () => { dragging = false; });
        })();

        // ===== REDIMENSIONNEMENT (RESIZE) =====
        (function initChatResize() {
            const cw     = document.getElementById('chatbotWindow');
            const handle = document.getElementById('chatResizeHandle');
            const msgs   = document.getElementById('chatMessages');
            let resizing = false, sx, sy, sw, sh, sm;

            function ensurePositioned() {
                if (!cw.classList.contains('cb-dragged')) {
                    const r = cw.getBoundingClientRect();
                    cw.style.left   = r.left + 'px';
                    cw.style.top    = r.top  + 'px';
                    cw.style.right  = 'auto';
                    cw.style.bottom = 'auto';
                    cw.classList.add('cb-dragged');
                }
            }

            handle.addEventListener('mousedown', (e) => {
                e.stopPropagation(); e.preventDefault();
                if (cw.classList.contains('cb-fullscreen')) return;
                ensurePositioned();
                resizing = true;
                sx = e.clientX; sy = e.clientY;
                sw = cw.offsetWidth;
                sm = parseInt(msgs.style.height) || msgs.offsetHeight;
                sh = cw.offsetHeight;
            });

            document.addEventListener('mousemove', (e) => {
                if (!resizing) return;
                const newW = Math.max(300, sw + (e.clientX - sx));
                const newH = Math.max(200, sm + (e.clientY - sy));
                cw.style.width    = newW + 'px';
                msgs.style.height = newH + 'px';
            });

            document.addEventListener('mouseup', () => { resizing = false; });
        })();

        function sendQuickMessage(text) {
            document.getElementById('chatInput').value = text;
            sendMessage();
        }

        // ===== IMAGE HANDLING =====
        function handleImageSelected(event) {
            const file = event.target.files[0];
            if (!file) return;
            pendingImageMime = file.type || "image/jpeg";
            const reader = new FileReader();
            reader.onload = (e) => {
                const dataUrl = e.target.result;
                pendingImageBase64 = dataUrl.split(',')[1]; // base64 only
                // Show preview
                document.getElementById('imagePreview').src = dataUrl;
                document.getElementById('imagePreviewZone').classList.remove('hidden');
                // Highlight camera button
                document.getElementById('cameraBtn').classList.add('bg-sun-300', 'border-sun-500');
            };
            reader.readAsDataURL(file);
            // Reset input so same file can be re-selected
            event.target.value = '';
        }

        function clearImage() {
            pendingImageBase64 = null;
            document.getElementById('imagePreviewZone').classList.add('hidden');
            document.getElementById('imagePreview').src = '';
            document.getElementById('cameraBtn').classList.remove('bg-sun-300', 'border-sun-500');
        }

        function lireDonneesCapteurs() {
            return {
                irradiance:  document.getElementById('irradianceValue')?.textContent || 'N/A',
                temperature: document.getElementById('panelTempValue')?.textContent || 'N/A',
                humidite:    document.getElementById('coolingHumidityValue')?.textContent || 'N/A',
                poussiere:   document.getElementById('dustValue')?.textContent || 'N/A',
                puissance:   document.getElementById('currentPower')?.textContent?.replace(/[^\d.]/g, '') || 'N/A',
                energie:     document.getElementById('dailyEnergy')?.textContent?.replace(/[^\d.]/g, '') || 'N/A',
            };
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const text = input.value.trim();
            const hasImage = !!pendingImageBase64;

            if (!text && !hasImage) return;

            const messages = document.getElementById('chatMessages');
            const time = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
            const displayText = text || "Analyser cette image";

            // Afficher message utilisateur (avec aperçu image si présent)
            const imageHtml = hasImage
                ? `<img src="data:${pendingImageMime};base64,${pendingImageBase64}" class="rounded-xl mt-2 max-h-40 object-cover border border-white/30" alt="photo envoyée">`
                : '';
            messages.innerHTML += `
                <div class="flex gap-3 justify-end">
                    <div class="bg-sun-500 rounded-2xl rounded-tr-sm p-3 max-w-[80%]">
                        <p class="text-sm text-white leading-relaxed">${displayText}</p>
                        ${imageHtml}
                        <span class="text-xs text-white/70 mt-1 block text-right">${time}</span>
                    </div>
                    <div class="w-8 h-8 rounded-lg bg-sun-100 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-user text-sun-600 text-xs"></i>
                    </div>
                </div>`;
            input.value = '';

            // Capture l'image en attente et réinitialise l'UI
            const imageBase64 = pendingImageBase64;
            const imageMime = pendingImageMime;
            if (hasImage) clearImage();

            messages.scrollTop = messages.scrollHeight;

            // Construire le contenu utilisateur (texte + image si présent)
            let userContent;
            if (imageBase64) {
                userContent = [
                    { type: "image_url", image_url: { url: `data:${imageMime};base64,${imageBase64}` } },
                    { type: "text", text: displayText }
                ];
            } else {
                userContent = displayText;
            }

            // Ajouter au contexte de conversation (texte seulement pour l'historique)
            chatHistory.push({ role: "user", content: displayText });

            // Indicateur de frappe
            messages.innerHTML += `
                <div id="typingIndicator" class="flex gap-3">
                    <div class="w-8 h-8 rounded-lg bg-solar-100 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-robot text-solar-600 text-xs"></i>
                    </div>
                    <div class="bg-solar-50 rounded-2xl rounded-tl-sm p-3">
                        <div class="flex gap-1">
                            <div class="w-2 h-2 rounded-full bg-solar-400 typing-dot"></div>
                            <div class="w-2 h-2 rounded-full bg-solar-400 typing-dot"></div>
                            <div class="w-2 h-2 rounded-full bg-solar-400 typing-dot"></div>
                        </div>
                    </div>
                </div>`;
            messages.scrollTop = messages.scrollHeight;

            // Appel Groq LLM
            appelGroq(displayText, imageBase64, imageMime).then(reponse => {
                const el = document.getElementById('typingIndicator');
                if (el) el.remove();

                // Ajouter réponse à l'historique
                chatHistory.push({ role: "assistant", content: reponse });

                // Garder l'historique limité à 20 messages pour économiser les tokens
                if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);

                messages.innerHTML += `
                    <div class="flex gap-3">
                        <div class="w-8 h-8 rounded-lg bg-solar-100 flex items-center justify-center flex-shrink-0">
                            <i class="fas fa-robot text-solar-600 text-xs"></i>
                        </div>
                        <div class="bg-solar-50 rounded-2xl rounded-tl-sm p-3 max-w-[80%]">
                            <p class="text-sm text-solar-800 leading-relaxed">${reponse.replace(/\n/g, '<br>')}</p>
                            <span class="text-xs text-solar-400 mt-1 block">${time}</span>
                        </div>
                    </div>`;
                messages.scrollTop = messages.scrollHeight;
            });
        }

        async function appelGroq(question, imageBase64 = null, imageMime = "image/jpeg") {
            const d = lireDonneesCapteurs();

            // Prompt système avec données capteurs en temps réel
            const systemPrompt = `Tu es DURASIA, un assistant IA expert en systèmes photovoltaïques intelligents.
Tu surveilles en temps réel le système DUR-2024-001 situé à Béni Mellal, Maroc (32.3°N, 6.4°W).

=== DONNÉES CAPTEURS EN TEMPS RÉEL ===
- Irradiance solaire    : ${d.irradiance} W/m²
- Température panneau  : ${d.temperature} °C
- Humidité système     : ${d.humidite} %
- Taux de poussière    : ${d.poussiere} %
- Puissance instantanée: ${d.puissance} kW
- Énergie journalière  : ${d.energie} kWh
- Heure locale         : ${new Date().toLocaleTimeString('fr-FR')}

=== CONTEXTE DU SYSTÈME ===
- Panneau solaire : 50W / 12V
- Supercondensateur : 20F / 8.1V (combinaison 3S2P de 6 cellules 10F/2.7V)
- Batterie : LiFePO4 12V avec protection par supercondensateur
- Système de refroidissement : couche hygroscopique MFC + polyacrylate + brumisation IA
- IA embarquée : XGBoost + GRU sur Raspberry Pi 4 pour prédiction des pics

=== INSTRUCTIONS ===
- Réponds toujours en français, de façon claire et concise
- Base tes analyses sur les données capteurs réelles ci-dessus
- Si une image est fournie, analyse-la en lien avec le système photovoltaïque (état du panneau, poussière, dommages, câblage, etc.)
- Si une valeur semble anormale, signale-le et explique pourquoi
- Tu peux donner des conseils de maintenance, d'optimisation et d'interprétation
- Reste dans le domaine du système solaire et de l'énergie renouvelable
- Sois précis et technique quand c'est nécessaire`;

            // Construire le contenu du dernier message utilisateur (avec image si présent)
            let lastUserContent;
            if (imageBase64) {
                lastUserContent = [
                    { type: "image_url", image_url: { url: `data:${imageMime};base64,${imageBase64}` } },
                    { type: "text", text: question }
                ];
            } else {
                lastUserContent = question;
            }

            // Construire les messages : historique (sans la dernière entrée user) + message actuel
            const historyWithoutLast = chatHistory.slice(0, -1); // le dernier a déjà été poussé dans sendMessage
            const apiMessages = [
                ...historyWithoutLast.slice(-9).map(m => ({ role: m.role, content: m.content })),
                { role: "user", content: lastUserContent }
            ];

            try {
                const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${GROQ_API_KEY}`
                    },
                    body: JSON.stringify({
                        model: GROQ_MODEL,
                        messages: [
                            { role: "system", content: systemPrompt },
                            ...apiMessages
                        ],
                        max_tokens: 500,
                        temperature: 0.7
                    })
                });

                if (!response.ok) {
                    const err = await response.json();
                    console.error('Groq error:', err);
                    return "⚠️ Erreur API. Vérifiez votre clé Groq et votre connexion internet.";
                }

                const data = await response.json();
                return data.choices[0].message.content;

            } catch (err) {
                console.error(err);
                return "⚠️ Impossible de contacter le LLM. Vérifiez votre connexion internet.";
            }
        }

        // ========== REALTIME UPDATES ==========
        function startRealtimeUpdates() {
            let compteurIA = 0;

            setInterval(() => {
                const irr = (850 + Math.random() * 100 - 50).toFixed(0);
                document.getElementById('irradianceValue').textContent = irr;
                document.getElementById('irradianceBar').style.width = (irr / 10) + '%';
                document.getElementById('irradianceStatus').textContent = irr > 800 ? 'Elevee' : irr > 500 ? 'Moyenne' : 'Faible';
                document.getElementById('irradianceStatus').className = 'font-medium px-2 py-0.5 rounded-full ' +
                    (irr > 800 ? 'text-sun-600 bg-sun-50' : irr > 500 ? 'text-amber-600 bg-amber-50' : 'text-blue-600 bg-blue-50');

                const temp = (42 + Math.random() * 4 - 2).toFixed(1);
                document.getElementById('panelTempValue').textContent = temp;
                document.getElementById('panelTempBar').style.width = (temp / 80 * 100) + '%';
                document.getElementById('panelTempStatus').textContent = temp > 55 ? 'Elevee' : temp > 45 ? 'Moderee' : 'Normale';

                const hum = Math.floor(35 + Math.random() * 6 - 3);
                document.getElementById('coolingHumidityValue').textContent = hum;
                document.getElementById('coolingHumidityBar').style.width = hum + '%';

                const dust = (8.2 + Math.random() * 1.5 - 0.75).toFixed(1);
                document.getElementById('dustValue').textContent = dust;
                document.getElementById('dustBar').style.width = dust + '%';
                document.getElementById('dustStatus').textContent = dust < 15 ? 'Faible' : dust < 30 ? 'Moyen' : 'Eleve';
                document.getElementById('dustStatus').className = 'font-medium px-2 py-0.5 rounded-full ' +
                    (dust < 15 ? 'text-green-600 bg-green-50' : dust < 30 ? 'text-amber-600 bg-amber-50' : 'text-red-600 bg-red-50');

                const power = (4.85 + Math.random() * 0.4 - 0.2).toFixed(2);
                document.getElementById('currentPower').innerHTML = power + '<span class="text-sm text-solar-400"> kW</span>';

                const currentDaily = parseFloat(document.getElementById('dailyEnergy').textContent);
                if (currentDaily < 32) {
                    document.getElementById('dailyEnergy').innerHTML = (currentDaily + 0.05).toFixed(1) + '<span class="text-sm text-solar-400"> kWh</span>';
                }

                updateProductionChart();

                // Toutes les 30 secondes → recommandation IA
                compteurIA++;
                if (compteurIA >= 10) {
                    compteurIA = 0;
                    genererRecommandationIA();
                }

            }, 3000);

            // Première recommandation immédiate au démarrage
            genererRecommandationIA();
        }

        async function genererRecommandationIA() {
            const d = lireDonneesCapteurs();
            const el = document.getElementById('aiRecommendation');
            if (!el) return;

            el.innerHTML = '<i class="fas fa-circle-notch fa-spin mr-2 opacity-60"></i><span class="opacity-60">Analyse IA en cours...</span>';

            const prompt = `Tu es DURASIA, un système IA de monitoring photovoltaïque intelligent.
Analyse ces données capteurs en temps réel et génère UNE recommandation courte (2-3 phrases maximum) :

- Irradiance solaire    : ${d.irradiance} W/m²
- Température panneau  : ${d.temperature} °C
- Humidité système     : ${d.humidite} %
- Taux de poussière    : ${d.poussiere} %
- Puissance instantanée: ${d.puissance} kW
- Énergie journalière  : ${d.energie} kWh
- Heure locale         : ${new Date().toLocaleTimeString('fr-FR')}

Règles :
- Si tout est normal → mentionne le point le plus positif et une prévision
- Température > 55°C = alerte surchauffe
- Poussière > 20% = recommander nettoyage
- Irradiance < 300 = conditions faibles
- Réponse directe en français, sans introduction`;

            try {
                const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${GROQ_API_KEY}`
                    },
                    body: JSON.stringify({
                        model: GROQ_MODEL,
                        messages: [{ role: "user", content: prompt }],
                        max_tokens: 150,
                        temperature: 0.8
                    })
                });

                if (!response.ok) return;
                const data = await response.json();
                const texte = data.choices[0].message.content;

                el.style.opacity = '0';
                el.style.transition = 'opacity 0.4s ease';
                setTimeout(() => {
                    el.textContent = texte;
                    el.style.opacity = '1';
                }, 400);

            } catch (err) {
                el.textContent = "Système opérationnel. Analyse temporairement indisponible.";
            }
        }

        // ========== CHARTS ==========
        let productionChart, predictionChart;
        let prodData = [];

        function initCharts() {
            for (let i = 0; i < 24; i++) {
                const hour = i;
                let val = 0;
                if (hour >= 6 && hour <= 18) {
                    val = Math.sin((hour - 6) / 12 * Math.PI) * 5.2;
                    val += (Math.random() - 0.5) * 0.5;
                }
                prodData.push(Math.max(0, val));
            }

            const ctx1 = document.getElementById('productionChart').getContext('2d');
            const gradient1 = ctx1.createLinearGradient(0, 0, 0, 300);
            gradient1.addColorStop(0, 'rgba(251, 191, 36, 0.4)');
            gradient1.addColorStop(1, 'rgba(251, 191, 36, 0.0)');

            productionChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: Array.from({length: 24}, (_, i) => i + 'h'),
                    datasets: [{
                        label: 'Puissance (kW)',
                        data: prodData,
                        borderColor: '#f59e0b',
                        backgroundColor: gradient1,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#f59e0b',
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: {
                        backgroundColor: 'rgba(20, 83, 45, 0.9)',
                        titleFont: { family: 'Inter', size: 12 },
                        bodyFont: { family: 'Inter', size: 13 },
                        padding: 12,
                        cornerRadius: 12,
                        displayColors: false
                    }},
                    scales: {
                        x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 10 }, color: '#86efac', maxTicksLimit: 8 } },
                        y: { grid: { color: 'rgba(20, 83, 45, 0.05)' }, ticks: { font: { family: 'Inter', size: 10 }, color: '#86efac' }, beginAtZero: true }
                    },
                    interaction: { intersect: false, mode: 'index' }
                }
            });

            const ctx2 = document.getElementById('predictionChart').getContext('2d');
            const gradient2 = ctx2.createLinearGradient(0, 0, 0, 200);
            gradient2.addColorStop(0, 'rgba(168, 85, 247, 0.3)');
            gradient2.addColorStop(1, 'rgba(168, 85, 247, 0.0)');

            predictionChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: ['8h', '10h', '12h', '14h', '14h30', '16h', '18h'],
                    datasets: [
                        {
                            label: 'Prediction IA',
                            data: [2.1, 3.8, 4.9, 5.1, 5.2, 4.3, 2.8],
                            borderColor: '#a855f7',
                            backgroundColor: gradient2,
                            borderWidth: 3,
                            borderDash: [5, 5],
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointBackgroundColor: '#a855f7',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        },
                        {
                            label: 'Reel',
                            data: [2.0, 3.7, 4.8, null, null, null, null],
                            borderColor: '#22c55e',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            tension: 0.4,
                            pointRadius: 4,
                            pointBackgroundColor: '#22c55e'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { font: { family: 'Inter', size: 11 }, usePointStyle: true, boxWidth: 8 } },
                        tooltip: {
                            backgroundColor: 'rgba(20, 83, 45, 0.9)',
                            titleFont: { family: 'Inter', size: 12 },
                            bodyFont: { family: 'Inter', size: 13 },
                            padding: 12,
                            cornerRadius: 12
                        }
                    },
                    scales: {
                        x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 10 }, color: '#86efac' } },
                        y: { grid: { color: 'rgba(20, 83, 45, 0.05)' }, ticks: { font: { family: 'Inter', size: 10 }, color: '#86efac' }, beginAtZero: true }
                    }
                }
            });
        }

        function updateProductionChart() {
            if (!productionChart) return;
            const currentHour = new Date().getHours();
            if (currentHour >= 6 && currentHour <= 18) {
                const val = Math.sin((currentHour - 6) / 12 * Math.PI) * 5.2 + (Math.random() - 0.5) * 0.3;
                productionChart.data.datasets[0].data[currentHour] = Math.max(0, val);
                productionChart.update('none');
            }
        }

        function initAdvancedCharts(type) {
            const commonOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { font: { family: 'Inter', size: 11 }, usePointStyle: true } } },
                scales: {
                    x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 10 }, color: '#86efac' } },
                    y: { grid: { color: 'rgba(20, 83, 45, 0.05)' }, ticks: { font: { family: 'Inter', size: 10 }, color: '#86efac' } }
                }
            };

            if (type === 'sensors') {
                const ctx1 = document.getElementById('advancedChart1')?.getContext('2d');
                if (ctx1) {
                    const g1 = ctx1.createLinearGradient(0, 0, 0, 200);
                    g1.addColorStop(0, 'rgba(251, 191, 36, 0.3)'); g1.addColorStop(1, 'rgba(251, 191, 36, 0.0)');
                    new Chart(ctx1, {
                        type: 'line',
                        data: {
                            labels: Array.from({length: 12}, (_, i) => (i*2+6) + 'h'),
                            datasets: [{
                                label: 'Irradiance (W/m2)',
                                data: [120, 350, 580, 750, 890, 920, 880, 720, 520, 310, 150, 50],
                                borderColor: '#f59e0b', backgroundColor: g1, borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3
                            }]
                        },
                        options: commonOptions
                    });
                }

                const ctx2 = document.getElementById('advancedChart2')?.getContext('2d');
                if (ctx2) {
                    const g2 = ctx2.createLinearGradient(0, 0, 0, 200);
                    g2.addColorStop(0, 'rgba(239, 68, 68, 0.3)'); g2.addColorStop(1, 'rgba(239, 68, 68, 0.0)');
                    new Chart(ctx2, {
                        type: 'line',
                        data: {
                            labels: Array.from({length: 12}, (_, i) => (i*2+6) + 'h'),
                            datasets: [{
                                label: 'Temperature (C)',
                                data: [25, 32, 38, 42, 45, 48, 46, 43, 40, 36, 30, 26],
                                borderColor: '#ef4444', backgroundColor: g2, borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3
                            }]
                        },
                        options: commonOptions
                    });
                }

                const ctx3 = document.getElementById('advancedChart3')?.getContext('2d');
                if (ctx3) {
                    const g3 = ctx3.createLinearGradient(0, 0, 0, 200);
                    g3.addColorStop(0, 'rgba(59, 130, 246, 0.3)'); g3.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
                    new Chart(ctx3, {
                        type: 'line',
                        data: {
                            labels: Array.from({length: 12}, (_, i) => (i*2+6) + 'h'),
                            datasets: [{
                                label: 'Humidite (%)',
                                data: [45, 42, 38, 35, 33, 32, 34, 36, 38, 40, 43, 46],
                                borderColor: '#3b82f6', backgroundColor: g3, borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3
                            }]
                        },
                        options: commonOptions
                    });
                }

                const ctx4 = document.getElementById('advancedChart4')?.getContext('2d');
                if (ctx4) {
                    new Chart(ctx4, {
                        type: 'bar',
                        data: {
                            labels: Array.from({length: 7}, (_, i) => 'J-' + (6-i)),
                            datasets: [{
                                label: 'Poussiere (%)',
                                data: [3.2, 4.1, 5.0, 5.8, 6.5, 7.3, 8.2],
                                backgroundColor: '#f59e0b', borderRadius: 8, borderSkipped: false
                            }]
                        },
                        options: commonOptions
                    });
                }

                const tbody = document.getElementById('sensorTableBody');
                if (tbody) {
                    let html = '';
                    for (let i = 0; i < 10; i++) {
                        const h = 8 + i;
                        const irr = Math.floor(100 + Math.random() * 800);
                        const temp = (25 + Math.random() * 20).toFixed(1);
                        const hum = Math.floor(30 + Math.random() * 20);
                        const dust = (5 + Math.random() * 5).toFixed(1);
                        const status = irr > 600 ? '<span class="text-green-600 bg-green-50 px-2 py-0.5 rounded-full text-xs">Optimal</span>' : 
                                       irr > 300 ? '<span class="text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full text-xs">Moyen</span>' :
                                       '<span class="text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full text-xs">Faible</span>';
                        html += `<tr class="border-b border-solar-100 hover:bg-solar-50/50 transition-all">
                            <td class="py-3 px-4 text-solar-800">${h}:00</td>
                            <td class="py-3 px-4 text-solar-800 font-medium">${irr}</td>
                            <td class="py-3 px-4 text-solar-800">${temp}</td>
                            <td class="py-3 px-4 text-solar-800">${hum}</td>
                            <td class="py-3 px-4 text-solar-800">${dust}</td>
                            <td class="py-3 px-4">${status}</td>
                        </tr>`;
                    }
                    tbody.innerHTML = html;
                }
            } else if (type === 'production') {
                const ctx = document.getElementById('advancedChartProd')?.getContext('2d');
                if (ctx) {
                    const g = ctx.createLinearGradient(0, 0, 0, 300);
                    g.addColorStop(0, 'rgba(34, 197, 94, 0.3)'); g.addColorStop(1, 'rgba(34, 197, 94, 0.0)');
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
                            datasets: [
                                {
                                    label: 'Production (kWh)',
                                    data: [26.4, 28.1, 24.7, 29.3, 27.8, 25.2, 28.4],
                                    backgroundColor: '#22c55e', borderRadius: 8, borderSkipped: false
                                },
                                {
                                    label: 'Objectif (kWh)',
                                    data: [28, 28, 28, 28, 28, 28, 32],
                                    type: 'line',
                                    borderColor: '#f59e0b', borderWidth: 2, borderDash: [5, 5], pointRadius: 0, fill: false
                                }
                            ]
                        },
                        options: commonOptions
                    });
                }
            } else if (type === 'weather') {
                const ctx1 = document.getElementById('advancedChartWeather1')?.getContext('2d');
                if (ctx1) {
                    const g = ctx1.createLinearGradient(0, 0, 0, 200);
                    g.addColorStop(0, 'rgba(251, 191, 36, 0.3)'); g.addColorStop(1, 'rgba(251, 191, 36, 0.0)');
                    new Chart(ctx1, {
                        type: 'line',
                        data: {
                            labels: Array.from({length: 12}, (_, i) => (i*2) + 'h'),
                            datasets: [{
                                label: 'Temperature (C)',
                                data: [18, 20, 23, 26, 28, 30, 32, 31, 29, 26, 22, 19],
                                borderColor: '#f59e0b', backgroundColor: g, borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3
                            }]
                        },
                        options: commonOptions
                    });
                }
                const ctx2 = document.getElementById('advancedChartWeather2')?.getContext('2d');
                if (ctx2) {
                    const g = ctx2.createLinearGradient(0, 0, 0, 200);
                    g.addColorStop(0, 'rgba(59, 130, 246, 0.3)'); g.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
                    new Chart(ctx2, {
                        type: 'line',
                        data: {
                            labels: Array.from({length: 12}, (_, i) => (i*2) + 'h'),
                            datasets: [{
                                label: 'Humidite (%)',
                                data: [55, 52, 48, 45, 42, 40, 38, 40, 43, 47, 50, 53],
                                borderColor: '#3b82f6', backgroundColor: g, borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3
                            }]
                        },
                        options: commonOptions
                    });
                }
            } else if (type === 'prediction') {
                const ctx = document.getElementById('advancedChartPred')?.getContext('2d');
                if (ctx) {
                    const g = ctx.createLinearGradient(0, 0, 0, 300);
                    g.addColorStop(0, 'rgba(168, 85, 247, 0.2)'); g.addColorStop(1, 'rgba(168, 85, 247, 0.0)');
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ['J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'Hier', "Aujourd'hui"],
                            datasets: [
                                {
                                    label: 'Prediction IA (kWh)',
                                    data: [25.8, 27.2, 24.1, 28.5, 26.9, 27.5, 31.8],
                                    borderColor: '#a855f7', backgroundColor: g, borderWidth: 3, borderDash: [5, 5],
                                    fill: true, tension: 0.3, pointRadius: 5, pointBackgroundColor: '#a855f7'
                                },
                                {
                                    label: 'Production Reelle (kWh)',
                                    data: [26.1, 27.0, 24.5, 28.2, 27.1, 27.8, null],
                                    borderColor: '#22c55e', backgroundColor: 'transparent', borderWidth: 2,
                                    tension: 0.3, pointRadius: 5, pointBackgroundColor: '#22c55e'
                                }
                            ]
                        },
                        options: commonOptions
                    });
                }
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeAdvancedModal();
                if (document.getElementById('sidebar').classList.contains('open')) toggleSidebar();
            }
        });
    </script>

    </script>
</body>
</html>
