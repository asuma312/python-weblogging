/**
 * Sistema de Modais
 * Biblioteca para criação e gerenciamento de modais
 */
class ModalSystem {
  constructor() {
    this.activeModal = null;
    this.defaultOptions = {
      width: '350px',
      animation: true,
      closeOnEsc: true,
      closeOnOverlayClick: true,
      theme: 'light'
    };

    // Inicializa ouvintes de eventos globais
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.activeModal && this.activeModal.options.closeOnEsc) {
        this.close();
      }
    });

    // Injetar estilos CSS
    this.injectStyles();
  }

  injectStyles() {
    if (document.getElementById('modal-system-styles')) return;

    const styleElement = document.createElement('style');
    styleElement.id = 'modal-system-styles';
    styleElement.textContent = `
      .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      .modal-overlay.visible {
        opacity: 1;
      }

      .modal-container {
        background-color: white;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        width: 350px;
        max-width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
        transform: translateY(-20px);
        opacity: 0;
        transition: transform 0.3s ease, opacity 0.3s ease;
      }

      .modal-container.visible {
        transform: translateY(0);
        opacity: 1;
      }

      .modal-title {
        margin: 0 0 16px 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: #333;
        text-align: center;
      }

      .modal-content {
        text-align: center;
      }

      .modal-message {
        margin-bottom: 20px;
        font-size: 1rem;
        color: #555;
        line-height: 1.5;
      }

      .modal-button {
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
      }

      .modal-button:hover {
        transform: translateY(-1px);
      }

      .modal-button:active {
        transform: translateY(1px);
      }

      .modal-button.primary {
        background-color: #4f46e5;
        color: white;
      }

      .modal-button.primary:hover {
        background-color: #4338ca;
      }

      .modal-button.error {
        background-color: #ef4444;
        color: white;
      }

      .modal-button.error:hover {
        background-color: #dc2626;
      }

      .modal-button.success {
        background-color: #10b981;
        color: white;
      }

      .modal-button.success:hover {
        background-color: #059669;
      }

      .modal-button-group {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 20px;
      }

      .modal-close {
        position: absolute;
        top: 12px;
        right: 12px;
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: #666;
        padding: 0;
        height: 24px;
        width: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.2s ease;
      }

      .modal-close:hover {
        color: #333;
      }

      /* Temas */
      .modal-container.dark {
        background-color: #1f2937;
        color: #f3f4f6;
      }

      .modal-container.dark .modal-title {
        color: #f3f4f6;
      }

      .modal-container.dark .modal-message {
        color: #d1d5db;
      }

      .modal-container.dark .modal-close {
        color: #9ca3af;
      }

      .modal-container.dark .modal-close:hover {
        color: #f3f4f6;
      }
    `;

    document.head.appendChild(styleElement);
  }

  create(options = {}) {
    // Mesclar opções com valores padrão
    const modalOptions = { ...this.defaultOptions, ...options };

    // Criar elementos base
    const overlay = document.createElement('div');
    overlay.classList.add('modal-overlay');
    overlay.id = 'modal-overlay';

    const modalContainer = document.createElement('div');
    modalContainer.classList.add('modal-container');
    if (modalOptions.theme) {
      modalContainer.classList.add(modalOptions.theme);
    }
    if (modalOptions.width) {
      modalContainer.style.width = modalOptions.width;
    }

    // Botão de fechar (X)
    const closeButton = document.createElement('button');
    closeButton.classList.add('modal-close');
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => this.close());

    // Título
    if (options.title) {
      const title = document.createElement('h2');
      title.classList.add('modal-title');
      title.textContent = options.title;
      modalContainer.appendChild(title);
    }

    // Conteúdo
    if (options.content) {
      const content = document.createElement('div');
      content.classList.add('modal-content');

      if (typeof options.content === 'string') {
        content.innerHTML = options.content;
      } else if (options.content instanceof HTMLElement) {
        content.appendChild(options.content);
      }

      modalContainer.appendChild(content);
    }

    modalContainer.appendChild(closeButton);
    overlay.appendChild(modalContainer);

    // Eventos
    if (modalOptions.closeOnOverlayClick) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.close();
        }
      });
    }

    // Armazenar estado
    this.activeModal = {
      overlay,
      container: modalContainer,
      options: modalOptions
    };

    return this;
  }

  show() {
    if (!this.activeModal) return;

    document.body.appendChild(this.activeModal.overlay);

    // Forçar reflow para garantir que as transições funcionem
    void this.activeModal.overlay.offsetWidth;

    // Aplicar classes para animar a entrada
    this.activeModal.overlay.classList.add('visible');
    this.activeModal.container.classList.add('visible');

    return this;
  }

  close() {
    if (!this.activeModal) return;

    const { overlay, container, options } = this.activeModal;

    // Animar saída
    overlay.classList.remove('visible');
    container.classList.remove('visible');

    // Remover após a animação
    setTimeout(() => {
      if (document.body.contains(overlay)) {
        document.body.removeChild(overlay);
      }
      this.activeModal = null;
    }, options.animation ? 300 : 0);

    return this;
  }
}

// Instância singleton do sistema de modais
const modalSystem = new ModalSystem();

/**
 * Funções helper para tipos comuns de modais
 */

function showErrorModal(message, title = 'Erro') {
  const content = document.createElement('div');

  const messageEl = document.createElement('p');
  messageEl.classList.add('modal-message');
  messageEl.textContent = message;

  const buttonGroup = document.createElement('div');
  buttonGroup.classList.add('modal-button-group');

  const okButton = document.createElement('button');
  okButton.classList.add('modal-button', 'error');
  okButton.textContent = 'OK';
  okButton.addEventListener('click', () => modalSystem.close());

  buttonGroup.appendChild(okButton);
  content.appendChild(messageEl);
  content.appendChild(buttonGroup);

  return modalSystem.create({
    title,
    content,
    theme: 'light'
  }).show();
}

function showSuccessModal(message, title = 'Sucesso') {
  const content = document.createElement('div');

  const messageEl = document.createElement('p');
  messageEl.classList.add('modal-message');
  messageEl.textContent = message;

  const buttonGroup = document.createElement('div');
  buttonGroup.classList.add('modal-button-group');

  const okButton = document.createElement('button');
  okButton.classList.add('modal-button', 'success');
  okButton.textContent = 'OK';
  okButton.addEventListener('click', () => modalSystem.close());

  buttonGroup.appendChild(okButton);
  content.appendChild(messageEl);
  content.appendChild(buttonGroup);

  return modalSystem.create({
    title,
    content,
    theme: 'light'
  }).show();
}

function showConfirmModal(message, onConfirm, onCancel, title = 'Confirmação') {
  const content = document.createElement('div');

  const messageEl = document.createElement('p');
  messageEl.classList.add('modal-message');
  messageEl.textContent = message;

  const buttonGroup = document.createElement('div');
  buttonGroup.classList.add('modal-button-group');

  const cancelButton = document.createElement('button');
  cancelButton.classList.add('modal-button');
  cancelButton.textContent = 'Cancelar';
  cancelButton.style.backgroundColor = '#e5e7eb';
  cancelButton.style.color = '#374151';
  cancelButton.addEventListener('click', () => {
    modalSystem.close();
    if (typeof onCancel === 'function') onCancel();
  });

  const confirmButton = document.createElement('button');
  confirmButton.classList.add('modal-button', 'primary');
  confirmButton.textContent = 'Confirmar';
  confirmButton.addEventListener('click', () => {
    modalSystem.close();
    if (typeof onConfirm === 'function') onConfirm();
  });

  buttonGroup.appendChild(cancelButton);
  buttonGroup.appendChild(confirmButton);
  content.appendChild(messageEl);
  content.appendChild(buttonGroup);

  return modalSystem.create({
    title,
    content
  }).show();
}

// Compatibilidade com código antigo
function CreateErrorModal(infoText, modalTitle) {
  return showErrorModal(infoText, modalTitle);
}