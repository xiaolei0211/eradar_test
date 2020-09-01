# 错误处理说明
def error_judgment_processing(can_frame):
    if can_frame is not None:
        if can_frame == '11':
            error = 'Error type:DiagExServiceNotSupported_Nrc11()'
        elif can_frame == '12':
            error = 'Error type:DiagExSubFunctionNotSupportedOrInvalidFormat_Nrc12()'
        elif can_frame == '13':
            error = 'Error type:DiagExIncorrectMessagelengthOrInvalidFormat_Nrc13()'
        elif can_frame == '14':
            error = 'Error type:DiagExResponseTooLong_Nrc14()'
        elif can_frame == '21':
            error = 'Error type:DiagExBusyRepeatRequest_Nrc21()'
        elif can_frame == '22':
            error = 'Error type:DiagExConditionsNotCorrect_Nrc22()'
        elif can_frame == '24':
            error = 'Error type:DiagExRequestSequenceError_Nrc24()'
        elif can_frame == '31':
            error = 'Error type:DiagExRequestOutofRange_Nrc31()'
        elif can_frame == '33':
            error = 'Error type:DiagExsecurityAccessError type:Denied_Nrc33()'
        elif can_frame == '35':
            error = 'Error type:DiagExInvalidkey_Nrc35()'
        elif can_frame == '36':
            error = 'Error type:DiagExceednumberOfAttempts_Nrc36()'
        elif can_frame == '37':
            error = 'Error type:DiagExRequiredTimeError type:DelayNotExpired_Nrc37()'
        elif can_frame == '70':
            error = 'Error type:DiagExUploadError type:DownloadNotAccepted_Nrc70()'
        elif can_frame == '71':
            error = 'Error type:DiagExTransferError type:DataSuspended_Nrc71()'
        elif can_frame == '72':
            error = 'Error type:DiagExGeneralProgrammingFailure_Nrc72()'
        elif can_frame == '73':
            error = 'Error type:DiagExWrongBlockSequenceCounter_Nrc73()'
        elif can_frame == '78':
            error = 'Error type:DiagExRequestCorrectlyReceivedResponsePending_Nrc78()'
        elif can_frame == '7E':
            error = 'Error type:DiagExSubFunctionNotSupportedInActiveSession_Nrc7E()'
        elif can_frame == '7F':
            error = 'Error type:DiagExSerivcenotSupportInActiveSession_Nrc7F()'
        elif can_frame == '87':
            error = 'Error type:DiagExError type:DefectWhileWriting_Nrc87()'
        elif can_frame == '92':
            error = 'Error type:DiagExSerivcenotSupport_voltageTooHigh_Nrc92()'
        elif can_frame == '93':
            error = 'Error type:DiagExSerivcenotSupport_voltageTooLow_Nrc93()'
        return error
