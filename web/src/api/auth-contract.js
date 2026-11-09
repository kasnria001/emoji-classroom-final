// Public registration implemented in app/api/v1/base/base.py.
// The server fixes the role; never substitute an administrator create-user API.
function isStrongPassword(value) {
  return (
    typeof value === 'string' &&
    [...value].length >= 8 &&
    [...value].length <= 128 &&
    /[A-Za-z]/.test(value) &&
    /\d/.test(value)
  )
}

function contractReady(contract) {
  return (
    typeof contract.path === 'string' &&
    contract.path.startsWith('/base/') &&
    typeof contract.passwordValidator === 'function'
  )
}

export const studentRegistrationContract = {
  path: '/base/register',
  // Match Python's password policy: 8..128 chars with at least one letter and one digit.
  passwordValidator: isStrongPassword,
}

export const teacherRegistrationContract = {
  path: '/base/register-teacher',
  passwordValidator: isStrongPassword,
}

// This endpoint derives the user exclusively from the authenticated request.
export const studentClassroomContract = { path: '/sessions/mine' }

export function registrationReady() {
  return contractReady(studentRegistrationContract)
}

export function teacherRegistrationReady() {
  return contractReady(teacherRegistrationContract)
}
