// @infra/validator/emailValidator/regexEmailValidator.ts

import type { EmailValidator } from '@domain/validation/emailValidator';

// An adapter for the EmailValidator using regex,
// but it could be any other implementation
export class RegexEmailValidator implements EmailValidator {
  regex: RegExp = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

  validate(email: string): boolean {
    return this.regex.test(email);
  };
};