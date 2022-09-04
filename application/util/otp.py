"""OTP Manage"""

import pyotp

# Counter based otp genrate and werification
class Hotp:

    _OTP = pyotp.HOTP('base32secret3232')

    # # Genrate otp
    def otp_gen(counter, otp=_OTP):
        return otp.at(counter)
    

    # # Verify otp
    def otp_verify(key, counter, otp=_OTP):
        return otp.verify(key, counter)