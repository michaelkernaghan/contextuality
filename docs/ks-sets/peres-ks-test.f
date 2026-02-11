C     Kochen-Specker coloring problem for N rays
C
C     Source: A. Peres, "Quantum Theory: Concepts and Methods"
C     (Kluwer, 1993), Appendix to Chapter 7, pages 209-211.
C     Reconstructed from scanned images.
C
C     Color code: 4 = unknown, 1 = green (yes), 0 = red (no)
C     Input file (INPUT.KS): pairs of orthogonal ray indices
C     Output file (OUTPUT.KS): coloring result
C
      PARAMETER (N=33)
      INTEGER P(N,N), X(N), Y(N), Z(N), C(N), L(N), OC(N,N)
      OPEN (8,FILE='INPUT.KS')
      OPEN (9,FILE='OUTPUT.KS')
      DO 10 I=1,N
      C(I)=4
10    CONTINUE
C     colors are unknown as yet
      DO 11 M=1,N*N
      READ (8,'(2I3)',END=12) I, J
      P(I,J)=1
      P(J,I)=1
11    CONTINUE
12    NTRIAD=0
      DO 13 I=1,N
      DO 13 J=I+1,N
      DO 13 K=J+1,N
      IF (P(I,J)+P(I,K)+P(J,K).NE.3) GOTO 13
      NTRIAD=NTRIAD+1
      X(NTRIAD)=I
      Y(NTRIAD)=J
      Z(NTRIAD)=K
13    CONTINUE
      LVL=0
C     Choose arbitrarily next green ray, whose number is NG
C     All other rays that are already colored are consistent
14    DO 15 NG=1,N
      IF (C(NG).EQ.4) THEN
        C(NG)=1
        GOTO 16
      ENDIF
15    CONTINUE
      WRITE (9,'(40I2)') C
C     A consistent coloring has been found
      STOP
16    LVL=LVL+1
      LAST=1
C     Last arbitrary assignment was to make a ray green
      L(LVL)=NG
C     This arbitrary assignment was made for ray NG
      DO 17 J=1,N
C     Record the situation after LVL arbitrary choices
17    OC(LVL,J)=C(J)
18    DO 19 J=1,N
C     All the rays orthogonal to a green one must be red
19    IF (P(NG,J).EQ.1) C(J)=0
20    DO 21 NT=1,NTRIAD
C     Now check whether there are three orthogonal red rays
      IF (C(X(NT))+C(Y(NT))+C(Z(NT)).EQ.0) GOTO 22
21    CONTINUE
      GOTO 25
22    IF (LVL+LAST.GT.0) GOTO 23
      WRITE (9,'('' No consistent coloring'')')
C     All options have been exhausted
      STOP
23    DO 24 J=1,N
C     Restore status quo at preceding branching
24    C(J)=OC(LVL,J)
      C(L(LVL))=0
      LAST=0
      GOTO 20
25    DO 26 NT=1,NTRIAD
C     Is there a triad with two red rays and a colorless ray?
C     If so, the colorless ray must be painted green
      IF (C(X(NT))+C(Y(NT))+C(Z(NT)).EQ.4) GOTO 27
26    CONTINUE
      GOTO 14
27    IF (C(X(NT)).EQ.4) THEN
        NG=X(NT)
        C(X(NT))=1
        GOTO 18
      ENDIF
      IF (C(Y(NT)).EQ.4) THEN
        NG=Y(NT)
        C(Y(NT))=1
        GOTO 18
      ENDIF
      IF (C(Z(NT)).EQ.4) THEN
        NG=Z(NT)
        C(Z(NT))=1
        GOTO 18
      ENDIF
      GOTO 14
      END
