class StudentRup:
    sql = 'students_rup.sql'
    pagination_key = 'RUPNREC'
    fields = {
        'NREC': Db('RUPNREC', str),
        'Year': Db('RYear', str),
    }
    required_params = ['id']


class StudentAddress:
    sql = 'students_address.sql'
    pagination_key = None
    fields = {
        "AddressType": {
            "ID": Db('ID', int),
            "AddressType": str
        },
        "country": {
            "ID": Db('AddrF0_ID', str),
            "country": Db('AddrF0', str)
        },
        "index": {
            "ID": Db('AddrF1_ID', str),
            "index": Db('AddrF1', str)
        },
        "region": {
            "ID": Db('AddrF2_ID', str),
            "region": Db('AddrF2', str)
        },
        "district": {
            "ID": Db('AddrF3_ID', str),
            "district": Db('AddrF3', str)
        },
        "city": {
            "ID": Db('AddrF4_ID', str),
            "city": Db('AddrF4', str)
        },
        "locality": {
            "ID": Db('AddrF5_ID', str),
            "locality": Db('AddrF5', str)
        },
        "street": {
            "ID": Db('AddrF6_id', str),
            "street": Db('AddrF6', str)
        },
        "homenumber": {
            "ID": Db('AddrF7_id', str),
            "homenumber": Db('AddrF7', str)
        },
        "corpnumber": {
            "ID": Db('AddrF8_id', str),
            "corpnumber": Db('AddrF8', str)
        },
        "flatnumber": {
            "ID": Db('AddrF9_id', str),
            "flatnumber": Db('AddrF9', str)
        },
        "kladrstreet": Db('kladrstreet', str)
    }
    required_params = ['id']


class Student:
    sql = 'students.sql'
    pagination_key = 'NREC'
    fields = {
        "NREC": Db('NREC', str),
        "PERSNREC": Db('Persnrec', str),
        "UID": Db('UID', str),
        "FullName": Db('FullName', str),
        "Status": {
            "ID": Db('Status_ID', str),
            "IDS": Db('Status_IDS', str),
            "Status": Db('STATUS', str)
        },
        "Baza": Db('baza', str),
        "Department": {
            "ID": Db('Department_ID', str),
            "IDS": Db('Department_IDS', str),
            "SHORT": Db('Department_Short', str),
            "Department": Db('Department', str)
        },
        "EduDirection": {
            "ID": Db('EduDirection_ID', str),
            "CODE": Db('EduDirection_CODE', str),
            "EduDirection": Db('EduDirection', str)
        },
        "EduProfile": {
            "ID": Db('EduProfile_ID', str),
            "EduProfile": Db('EduProfile', str)
        },
        "EduQual": {
            "ID": Db('EduQual_ID', str),
            "EduQual": Db('EduQual', str)
        },
        "EduLevel": {
            "ID": Db('EduLevel_ID', str),
            "EduLevel": Db('EduLevel', str)
        },
        "StudyForm": {
            "ID": Db('StudyForm_ID', str),
            "StudyForm": Db('StudyForm', str)
        },
        "Year": Db('StYear', str),
        "AppDate": Db('AppDate', str),
        "AdmissionYear": Db('AdmissionYear', str),
        "Group": {
            "ID": Db('Group_ID', str),
            "Group": Db('Group_Name', str)
        },
        "SubGroup": {
            "ID": Db('SubGroup_ID', str),
            "SubGroup": Db('SubGroup', str)
        },
        "DisDate": Db('DisDate', str),
        "ADMISSIONBUPNREC": Db('ADMISSIONBUPNREC', str),
        "ADMISSIONRUPNREC": Db('ADMISSIONRUPNREC', str),
        "BUPNREC": Db('BUPNREC', str),
        "RUPNREC": Db('RUPNREC', str),
        'RUPS': Select('StudentRup', id='ID'),
        "Borndate": Db('Borndate', str),
        "Sex": Db('Sex', str),
        "Localiz": Db('Localiz', str),
        "Gr": {
            "ID": Db('Gr_ID', str),
            "Gr": Db('Gr', str)
        },
        "FIN": {
            "ID": Db('FIN_ID', str),
            "FIN": Db('FIN', str)
        },
        "IsFromOtherVuz": Db('IsFromOtherVuz', str),
        "IsCP": Db('IsCp', str),
        "Person": {
            "LastName": Db('LastName', str),
            "FirstName": Db('FirstName', str),
            "PatrName": Db('PatrName', str),
            "IdentityDoc": {
                "ID": Db('Passp_Id', str),
                "IdentityDoc": Db('IdentityDoc', str)
            },
            "DocSerie": Db('DocSerie', str),
            "DocNumber": Db('DocNumber', str),
            "DocDate": Db('DocDate', str),
            "DocOrg": Db('DocOrg', str),
            "BirthPlace": Db('BirthPlace', str),
            "Phone": Db('phone', str),
            "Email": Db('email', str),
            "Photo": Db('IsCp', str),
            "IsPersonalDataAgreement": Db('IsPersonalDataAgreement', str),
            'Addresses': Select('StudentAddress', id='ID')
        },
        "Modified": Db('Modified', str)
    }

    params = [
        Exact('baza', 'UStudent.F$WARCH'),
        Exact('status', 'UStudent.F$WARCH'),
        Custom('id', 'UStudent.f$nrec = convert(binary(8),convert(bigInt,0x8000000000000000)+convert(bigint,\'%s\'))'),
        Custom('date',
               ' UStudent.F$APPDATE>=[dbo].ToAtlDate(CONVERT(date, \'%s\' ,103)) and UStudent.F$DisDATE<=[dbo].ToAtlDate(CONVERT(date, \'%s\' , 103)) ')
    ]
