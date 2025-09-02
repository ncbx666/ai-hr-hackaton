import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Registration.css';

interface FormData {
  firstName: string;
  lastName: string;
  middleName: string;
  email: string;
  phone: string;
  privacyConsent: boolean;
}

const Registration: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    middleName: '',
    email: '',
    phone: '',
    privacyConsent: false
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<FormData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<FormData> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'Имя обязательно для заполнения';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Фамилия обязательна для заполнения';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email обязателен для заполнения';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Некорректный формат email';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Телефон обязателен для заполнения';
    }

    if (!formData.privacyConsent) {
      newErrors.privacyConsent = true as any;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Очищаем ошибку для поля при изменении
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Имитация отправки данных на сервер
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // После успешной регистрации переходим к ожиданию
      navigate(`/candidate/${sessionId}/waiting`);
    } catch (error) {
      alert('Ошибка при регистрации. Попробуйте еще раз.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-page">
      <div className="registration-container">
        <div className="header">
          <h1>Регистрация</h1>
          <p>Введите ваши данные для начала собеседования</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="lastName">
                Фамилия <span className="required">*</span>
              </label>
              <input
                type="text"
                id="lastName"
                value={formData.lastName}
                onChange={(e) => handleInputChange('lastName', e.target.value)}
                className={errors.lastName ? 'error' : ''}
                placeholder="Введите фамилию"
              />
              {errors.lastName && <span className="error-text">{errors.lastName}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="firstName">
                Имя <span className="required">*</span>
              </label>
              <input
                type="text"
                id="firstName"
                value={formData.firstName}
                onChange={(e) => handleInputChange('firstName', e.target.value)}
                className={errors.firstName ? 'error' : ''}
                placeholder="Введите имя"
              />
              {errors.firstName && <span className="error-text">{errors.firstName}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="middleName">Отчество</label>
            <input
              type="text"
              id="middleName"
              value={formData.middleName}
              onChange={(e) => handleInputChange('middleName', e.target.value)}
              placeholder="Введите отчество (необязательно)"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">
              Email <span className="required">*</span>
            </label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className={errors.email ? 'error' : ''}
              placeholder="example@domain.com"
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="phone">
              Телефон <span className="required">*</span>
            </label>
            <input
              type="tel"
              id="phone"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              className={errors.phone ? 'error' : ''}
              placeholder="+7 (999) 123-45-67"
            />
            {errors.phone && <span className="error-text">{errors.phone}</span>}
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.privacyConsent}
                onChange={(e) => handleInputChange('privacyConsent', e.target.checked)}
                className={errors.privacyConsent ? 'error' : ''}
              />
              <span className="checkmark"></span>
              <span className="checkbox-text">
                Я согласен на обработку персональных данных в соответствии с 
                <a href="#" target="_blank"> политикой конфиденциальности</a>
                <span className="required"> *</span>
              </span>
            </label>
            {errors.privacyConsent && (
              <span className="error-text">Необходимо согласие на обработку данных</span>
            )}
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="submit-btn"
              disabled={loading}
            >
              {loading ? 'Регистрация...' : 'Далее'}
            </button>
          </div>
        </form>

        <div className="form-info">
          <p>
            <strong>Важно:</strong> Ваши данные будут использованы только в рамках данного собеседования 
            и не будут переданы третьим лицам.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Registration;
