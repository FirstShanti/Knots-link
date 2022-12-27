const encryptData = (payload, k, i) => {
    // var _k = CryptoJS.enc.Base64.parse(_.join(_.slice(k, 0, 16), separator=''))
    // var _i = CryptoJS.enc.Utf8.parse(_.join(_.slice(i, 0, 16), separator=''));
    console.log(k)
    console.log(i)
    // var _p = CryptoJS.enc.Base64.parse(payload)
    var _k = CryptoJS.enc.Utf8.parse(k)
    var _i = CryptoJS.enc.Utf8.parse(_.join(_.slice(i, 0, 16), separator=''));
    return CryptoJS.AES.encrypt(payload, _k, {iv: _i, mode: CryptoJS.mode.CBC}).toString(); 
}
