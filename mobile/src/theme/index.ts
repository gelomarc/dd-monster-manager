export const colors = {
  primary: '#E40712',
  primaryDark: '#B30000',
  background: '#242527',
  surface: '#383838',
  surfaceDark: '#1A1A1A',
  text: '#FFFFFF',
  textSecondary: '#CCCCCC',
  border: '#666666',
  success: '#28a745',
  danger: '#DC3545',
  warning: '#FFC107',
  gold: '#B89B46',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const typography = {
  h1: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
  },
  h2: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
  },
  body: {
    fontSize: 16,
    color: colors.text,
  },
  caption: {
    fontSize: 14,
    color: colors.textSecondary,
  },
};

export const shadows = {
  small: {
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  medium: {
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
  },
};

export default {
  colors,
  spacing,
  typography,
  shadows,
}; 