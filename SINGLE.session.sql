INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (1, 'AA');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (2, 'AB');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (3, 'AC');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (4, 'AD');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (5, 'AE');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (6, 'AF');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (7, 'AG');
INSERT INTO COMPOSITION (COM_ID, COM_NM)
VALUES (8, 'AH');


INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    1,
    1,
    'DESCRIPT : AA-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    1,
    2,
    'DESCRIPT : AA-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    1,
    3,
    'DESCRIPT : AA-3'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    2,
    1,
    'DESCRIPT : AB-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    2,
    2,
    'DESCRIPT : AB-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    3,
    1,
    'DESCRIPT : AC-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    3,
    2,
    'DESCRIPT : AC-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    4,
    1,
    'DESCRIPT : AD-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    4,
    2,
    'DESCRIPT : AD-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    5,
    1,
    'DESCRIPT : AE-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    5,
    2,
    'DESCRIPT : AE-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    6,
    1,
    'DESCRIPT : AF-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    6,
    2,
    'DESCRIPT : AF-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    7,
    1,
    'DESCRIPT : AG-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    7,
    2,
    'DESCRIPT : AG-2'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    8,
    1,
    'DESCRIPT : AH-1'
  );

INSERT INTO DESCRIPTION (COM_ID, DESC_ID, DESCRIPT)
VALUES (
    8,
    2,
    'DESCRIPT : AH-2'
  );


INSERT INTO NUMBER_CODE (CODE, COM_NUMBER, COM_ID)
VALUES (
  209703,
  1,
  3
);

INSERT INTO NUMBER_CODE (CODE, COM_NUMBER, COM_ID)
VALUES (
  209703,
  2,
  1
);

INSERT INTO NUMBER_CODE (CODE, COM_NUMBER, COM_ID)
VALUES (
  209704,
  1,
  3
);

INSERT INTO NUMBER_CODE (CODE, COM_NUMBER, COM_ID)
VALUES (
  209704,
  2,
  1
);

SELECT A.CODE, A.COM_NUMBER, C.DESC_ID FROM NUMBER_CODE A
LEFT JOIN DESCRIPTION C ON C.COM_ID = A.COM_ID
WHERE A.CODE = 209703
ORDER BY C.COM_ID,  C.DESC_ID;


SELECT COM_NM FROM COMPOSITION;



SELECT C.COM_NM, A.DESC_ID, A.DESCRIPT FROM DESCRIPTION A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID ORDER BY C.COM_ID